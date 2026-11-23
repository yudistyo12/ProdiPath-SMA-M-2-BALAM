import logging

from fastapi import APIRouter, HTTPException

from backend.database import get_db_connection
from backend.schemas.models import PredictionRequest
from backend.services.saw import rank_majors

router = APIRouter(prefix="/api/predict", tags=["predict"])
logger = logging.getLogger(__name__)


@router.post("/")
def predict_major(request: PredictionRequest):
    input_data = request.model_dump()
    nama = input_data["nama"].strip()
    if not nama:
        raise HTTPException(status_code=422, detail="Nama siswa wajib diisi.")

    conn = get_db_connection()
    if not conn:
        raise HTTPException(
            status_code=503,
            detail="Database belum tersedia. Data referensi SPK tidak dapat diakses.",
        )

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT jurusan_sma, nilai_matematika, nilai_sains, nilai_sosial,
                   nilai_bahasa, minat_teknologi, minat_seni,
                   minat_komunikasi, kemampuan_analitis, rekomendasi_jurusan
            FROM questionnaire_data
            WHERE sumber_data = 'dataset'
            """
        )
        reference_rows = cursor.fetchall()
        try:
            rankings = rank_majors(input_data, reference_rows)
        except ValueError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        recommendation = rankings[0]["program_studi"]
        cursor.execute(
            """
            INSERT INTO questionnaire_data
            (nisn, nama, jurusan_sma, nilai_matematika, nilai_sains, nilai_sosial,
             nilai_bahasa, minat_teknologi, minat_seni, minat_komunikasi,
             kemampuan_analitis, rekomendasi_jurusan, sumber_data, persetujuan_data)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'kuesioner_web', %s)
            ON DUPLICATE KEY UPDATE
            nama=VALUES(nama), jurusan_sma=VALUES(jurusan_sma),
            nilai_matematika=VALUES(nilai_matematika), nilai_sains=VALUES(nilai_sains),
            nilai_sosial=VALUES(nilai_sosial), nilai_bahasa=VALUES(nilai_bahasa),
            minat_teknologi=VALUES(minat_teknologi), minat_seni=VALUES(minat_seni),
            minat_komunikasi=VALUES(minat_komunikasi),
            kemampuan_analitis=VALUES(kemampuan_analitis),
            rekomendasi_jurusan=VALUES(rekomendasi_jurusan),
            sumber_data='kuesioner_web',
            persetujuan_data=VALUES(persetujuan_data)
            """,
            (
                input_data["nisn"],
                nama,
                input_data["jurusan_sma"],
                input_data["nilai_matematika"],
                input_data["nilai_sains"],
                input_data["nilai_sosial"],
                input_data["nilai_bahasa"],
                input_data["minat_teknologi"],
                input_data["minat_seni"],
                input_data["minat_komunikasi"],
                input_data["kemampuan_analitis"],
                recommendation,
                input_data["persetujuan_data"],
            ),
        )
        conn.commit()
    except HTTPException:
        raise
    except Exception as exc:
        conn.rollback()
        logger.exception(
            "Failed to calculate or save recommendation for NISN %s",
            input_data["nisn"],
        )
        raise HTTPException(
            status_code=500,
            detail="Perhitungan SPK atau penyimpanan data gagal diproses.",
        ) from exc
    finally:
        cursor.close()
        conn.close()

    return {
        "nisn": input_data["nisn"],
        "nama": nama,
        "prediksi": recommendation,
        "metode": "SAW",
        "bobot_kriteria": 1 / 9,
        "peringkat": rankings[:3],
        "catatan_metode": (
            "Skor memakai bobot awal yang sama untuk 9 kriteria dan profil "
            "program studi dari data berlabel dataset. Bobot dan data rujukan "
            "perlu divalidasi bersama guru BK. Skor menunjukkan kecocokan, "
            "bukan peluang keberhasilan atau akurasi rekomendasi."
        ),
        "tersimpan": True,
    }

import io

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.database import get_db_connection
from backend.routes.auth import require_admin

router = APIRouter(prefix="/api/dataset", tags=["dataset"])

SCORE_COLUMNS = [
    "nilai_matematika",
    "nilai_sains",
    "nilai_sosial",
    "nilai_bahasa",
]
LIKERT_COLUMNS = [
    "minat_teknologi",
    "minat_seni",
    "minat_komunikasi",
    "kemampuan_analitis",
]
REQUIRED_COLUMNS = [
    "nisn",
    "nama",
    "jurusan_sma",
    *SCORE_COLUMNS,
    *LIKERT_COLUMNS,
    "rekomendasi_jurusan",
]
MAJOR_TRACKS = {"IPA", "IPS", "Bahasa"}


@router.post("/import", dependencies=[Depends(require_admin)])
async def import_dataset(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File harus berformat CSV.")

    contents = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(contents), dtype={"nisn": str}, encoding="utf-8-sig")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Gagal membaca CSV: {exc}") from exc

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Kolom CSV tidak lengkap. Kolom yang kurang: {', '.join(missing_columns)}",
        )

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Koneksi database gagal.")

    query = """
        INSERT INTO questionnaire_data
        (nisn, nama, jurusan_sma, nilai_matematika, nilai_sains, nilai_sosial,
         nilai_bahasa, minat_teknologi, minat_seni, minat_komunikasi,
         kemampuan_analitis, rekomendasi_jurusan, sumber_data, persetujuan_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'dataset', FALSE)
        ON DUPLICATE KEY UPDATE
        nama=VALUES(nama), jurusan_sma=VALUES(jurusan_sma),
        nilai_matematika=VALUES(nilai_matematika), nilai_sains=VALUES(nilai_sains),
        nilai_sosial=VALUES(nilai_sosial), nilai_bahasa=VALUES(nilai_bahasa),
        minat_teknologi=VALUES(minat_teknologi), minat_seni=VALUES(minat_seni),
        minat_komunikasi=VALUES(minat_komunikasi),
        kemampuan_analitis=VALUES(kemampuan_analitis),
        rekomendasi_jurusan=VALUES(rekomendasi_jurusan),
        sumber_data='dataset',
        persetujuan_data=FALSE
    """

    errors = []
    success_count = 0
    cursor = conn.cursor()
    try:
        for index, row in df.iterrows():
            line = index + 2
            try:
                nisn = str(row["nisn"]).strip()
                nama = str(row["nama"]).strip()
                jurusan_sma = str(row["jurusan_sma"]).strip()
                recommendation = str(row["rekomendasi_jurusan"]).strip()
                if not nisn or nisn.lower() == "nan" or not nama or nama.lower() == "nan":
                    raise ValueError("NISN dan nama wajib diisi.")
                if jurusan_sma not in MAJOR_TRACKS:
                    raise ValueError("jurusan_sma harus IPA, IPS, atau Bahasa.")
                if not recommendation or recommendation.lower() == "nan":
                    raise ValueError("rekomendasi_jurusan wajib diisi.")

                values = []
                for column in SCORE_COLUMNS:
                    value = float(row[column])
                    if not value.is_integer() or not 0 <= value <= 100:
                        raise ValueError(f"{column} harus bilangan bulat 0-100.")
                    values.append(int(value))
                for column in LIKERT_COLUMNS:
                    value = float(row[column])
                    if not value.is_integer() or not 1 <= value <= 5:
                        raise ValueError(f"{column} harus bilangan bulat 1-5.")
                    values.append(int(value))

                cursor.execute(
                    query,
                    (nisn, nama, jurusan_sma, *values, recommendation),
                )
                success_count += 1
            except (TypeError, ValueError) as exc:
                errors.append(f"Baris {line}: {exc}")

        conn.commit()
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan dataset: {exc}") from exc
    finally:
        cursor.close()
        conn.close()

    return {
        "message": f"Berhasil mengimpor {success_count} data siswa.",
        "errors": errors,
        "success_count": success_count,
    }

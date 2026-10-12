import logging
import os

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException

from backend.database import get_db_connection
from backend.schemas.models import PredictionRequest
from ml.preprocessing import FEATURES

router = APIRouter(prefix="/api/predict", tags=["predict"])
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "model_jurusan.pkl")
ENCODER_PATH = os.path.join(PROJECT_ROOT, "models", "label_encoder.pkl")


@router.post("/")
def predict_major(request: PredictionRequest):
    if not os.path.exists(MODEL_PATH) or not os.path.exists(ENCODER_PATH):
        raise HTTPException(
            status_code=503,
            detail="Model rekomendasi belum tersedia. Latih model terlebih dahulu.",
        )

    try:
        model = joblib.load(MODEL_PATH)
        label_encoder = joblib.load(ENCODER_PATH)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Model rekomendasi gagal dimuat: {exc}",
        ) from exc

    input_data = request.model_dump()
    nama = input_data["nama"].strip()
    if not nama:
        raise HTTPException(status_code=422, detail="Nama siswa wajib diisi.")

    features = pd.DataFrame([{feature: input_data[feature] for feature in FEATURES}])

    try:
        predicted_class = model.predict(features)[0]
        recommendation = label_encoder.inverse_transform([predicted_class])[0]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediksi gagal diproses: {exc}",
        ) from exc

    conn = get_db_connection()
    if not conn:
        raise HTTPException(
            status_code=503,
            detail="Database belum tersedia. Jawaban belum dapat disimpan; silakan coba lagi.",
        )

    cursor = conn.cursor()
    try:
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
    except Exception as exc:
        conn.rollback()
        logger.exception("Failed to save questionnaire for NISN %s", input_data["nisn"])
        raise HTTPException(
            status_code=500,
            detail="Rekomendasi berhasil dihitung, tetapi data siswa gagal disimpan.",
        ) from exc
    finally:
        cursor.close()
        conn.close()

    return {
        "nisn": input_data["nisn"],
        "nama": nama,
        "prediksi": recommendation,
        "tersimpan": True,
    }

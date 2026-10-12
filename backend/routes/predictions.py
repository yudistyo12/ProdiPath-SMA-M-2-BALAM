from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import joblib
import numpy as np
from backend.database import get_db
from backend.models.models import User, Prediction, Student
from backend.schemas.schemas import PredictionInput, PredictionResult
from backend.services.auth import get_current_user

router = APIRouter(prefix="/api/predict", tags=["Prediction"])

FEATURES = [
    'konsistensi_belajar', 'manajemen_waktu', 'penyelesaian_tugas',
    'pemahaman_materi', 'konsentrasi_belajar', 'persiapan_ujian',
    'keaktifan_pembelajaran', 'motivasi_belajar', 'pemanfaatan_waktu_belajar'
]

# Load model
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
model_path = os.path.join(base_dir, 'models', 'model_performa.pkl')
encoder_path = os.path.join(base_dir, 'models', 'label_encoder.pkl')

model = None
label_encoder = None

try:
    if os.path.exists(model_path):
        model = joblib.load(model_path)
    if os.path.exists(encoder_path):
        label_encoder = joblib.load(encoder_path)
except Exception as e:
    print(f"Warning: Gagal memuat model: {e}")


@router.post("", response_model=PredictionResult)
def predict_performance(
    input_data: PredictionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    global model, label_encoder

    if model is None or label_encoder is None:
        # Coba load ulang
        try:
            model = joblib.load(model_path)
            label_encoder = joblib.load(encoder_path)
        except Exception:
            raise HTTPException(status_code=503, detail="Model AI belum tersedia. Latih model terlebih dahulu.")

    # Siapkan input sesuai urutan fitur training
    features = np.array([[
        input_data.konsistensi_belajar,
        input_data.manajemen_waktu,
        input_data.penyelesaian_tugas,
        input_data.pemahaman_materi,
        input_data.konsentrasi_belajar,
        input_data.persiapan_ujian,
        input_data.keaktifan_pembelajaran,
        input_data.motivasi_belajar,
        input_data.pemanfaatan_waktu_belajar
    ]])

    try:
        prediction_encoded = model.predict(features)[0]
        prediction_label = label_encoder.inverse_transform([prediction_encoded])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error prediksi: {str(e)}")

    # Simpan ke database jika ada student_id
    if input_data.student_id:
        resp = db.query(Student).filter(Student.id == input_data.student_id).first()
        if resp:
            pred = Prediction(
                student_id=resp.id,
                predicted_performance=prediction_label
            )
            db.add(pred)
            db.commit()

    return PredictionResult(
        predicted_performance=prediction_label,
        student_id=input_data.student_id
    )

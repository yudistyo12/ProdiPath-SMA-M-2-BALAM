"""
Route khusus mahasiswa: lihat profil sendiri, isi kuesioner, lihat hasil prediksi.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os, joblib, numpy as np
from backend.database import get_db
from backend.models.models import Student, QuestionnaireData, Prediction, User
from backend.schemas.schemas import QuestionnaireBase
from backend.services.auth import get_current_user

router = APIRouter(prefix="/api/mahasiswa", tags=["Mahasiswa"])

FEATURES = [
    'konsistensi_belajar', 'manajemen_waktu', 'penyelesaian_tugas',
    'pemahaman_materi', 'konsentrasi_belajar', 'persiapan_ujian',
    'keaktifan_pembelajaran', 'motivasi_belajar', 'pemanfaatan_waktu_belajar'
]

# Load model
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
model_path = os.path.join(base_dir, 'models', 'model_performa.pkl')
encoder_path = os.path.join(base_dir, 'models', 'label_encoder.pkl')


def _get_student(user: User, db: Session) -> Student:
    """Cari data mahasiswa berdasarkan username (NPM) user yang login."""
    student = db.query(Student).filter(Student.npm == user.username).first()
    if not student:
        raise HTTPException(status_code=404, detail="Data mahasiswa belum terdaftar di sistem.")
    return student


@router.get("/profil")
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mahasiswa melihat data diri sendiri + kuesioner + prediksi."""
    student = _get_student(current_user, db)

    questionnaire_data = None
    if student.questionnaire:
        q = student.questionnaire
        questionnaire_data = {
            "konsistensi_belajar": q.konsistensi_belajar,
            "manajemen_waktu": q.manajemen_waktu,
            "penyelesaian_tugas": q.penyelesaian_tugas,
            "pemahaman_materi": q.pemahaman_materi,
            "konsentrasi_belajar": q.konsentrasi_belajar,
            "persiapan_ujian": q.persiapan_ujian,
            "keaktifan_pembelajaran": q.keaktifan_pembelajaran,
            "motivasi_belajar": q.motivasi_belajar,
            "pemanfaatan_waktu_belajar": q.pemanfaatan_waktu_belajar,
            "performa_belajar": q.performa_belajar,
        }

    latest_prediction = None
    if student.predictions:
        last = student.predictions[-1]
        latest_prediction = {
            "predicted_performance": last.predicted_performance,
            "created_at": str(last.created_at),
        }

    return {
        "npm": student.npm,
        "program_studi": student.program_studi,
        "semester": student.semester,
        "questionnaire": questionnaire_data,
        "prediction": latest_prediction,
    }


@router.post("/kuesioner")
def submit_questionnaire(
    data: QuestionnaireBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mahasiswa mengisi/memperbarui kuesioner kebiasaan belajar mereka sendiri."""
    student = _get_student(current_user, db)

    # Hitung performa_belajar otomatis dari rata-rata skor
    scores = [
        data.konsistensi_belajar, data.manajemen_waktu, data.penyelesaian_tugas,
        data.pemahaman_materi, data.konsentrasi_belajar, data.persiapan_ujian,
        data.keaktifan_pembelajaran, data.motivasi_belajar, data.pemanfaatan_waktu_belajar
    ]
    avg = sum(scores) / len(scores)
    if avg >= 3.8:
        performa = "Tinggi"
    elif avg >= 2.6:
        performa = "Sedang"
    else:
        performa = "Rendah"

    if student.questionnaire:
        # Update kuesioner yang sudah ada
        q = student.questionnaire
        for key, val in data.model_dump().items():
            setattr(q, key, val)
        q.performa_belajar = performa
    else:
        # Buat kuesioner baru
        q_data = data.model_dump()
        q_data['performa_belajar'] = performa
        q_data['student_id'] = student.id
        q = QuestionnaireData(**q_data)
        db.add(q)

    db.commit()
    db.refresh(student)

    # Langsung jalankan prediksi AI setelah mengisi kuesioner
    try:
        model = joblib.load(model_path)
        label_encoder = joblib.load(encoder_path)

        features = np.array([[
            data.konsistensi_belajar, data.manajemen_waktu, data.penyelesaian_tugas,
            data.pemahaman_materi, data.konsentrasi_belajar, data.persiapan_ujian,
            data.keaktifan_pembelajaran, data.motivasi_belajar, data.pemanfaatan_waktu_belajar
        ]])

        prediction_encoded = model.predict(features)[0]
        prediction_label = label_encoder.inverse_transform([prediction_encoded])[0]

        # Simpan prediksi
        pred = Prediction(
            student_id=student.id,
            predicted_performance=prediction_label
        )
        db.add(pred)
        db.commit()

        return {
            "message": "Kuesioner berhasil disimpan dan prediksi AI berhasil dijalankan!",
            "performa_kuesioner": performa,
            "prediksi_ai": prediction_label,
        }
    except Exception as e:
        return {
            "message": "Kuesioner berhasil disimpan, namun prediksi AI gagal.",
            "performa_kuesioner": performa,
            "prediksi_ai": None,
            "error": str(e)
        }

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_db_connection
from backend.routes.auth import require_admin
from backend.schemas.models import QuestionnaireData

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("/", response_model=List[QuestionnaireData], dependencies=[Depends(require_admin)])
def get_students(search: Optional[str] = None, jurusan_sma: Optional[str] = None):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Koneksi database gagal.")

    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM questionnaire_data WHERE 1=1"
    params = []
    if search:
        query += " AND (nisn LIKE %s OR nama LIKE %s OR rekomendasi_jurusan LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if jurusan_sma:
        query += " AND jurusan_sma = %s"
        params.append(jurusan_sma)
    query += " ORDER BY nama"

    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@router.get("/{nisn}", response_model=QuestionnaireData, dependencies=[Depends(require_admin)])
def get_student(nisn: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Koneksi database gagal.")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM questionnaire_data WHERE nisn = %s", (nisn,))
        student = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not student:
        raise HTTPException(status_code=404, detail="Data siswa tidak ditemukan.")
    return student


@router.delete("/{nisn}", dependencies=[Depends(require_admin)])
def delete_student(nisn: str):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Koneksi database gagal.")

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM questionnaire_data WHERE nisn = %s", (nisn,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Data siswa tidak ditemukan.")
    except HTTPException:
        conn.rollback()
        raise
    except Exception as exc:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Gagal menghapus data siswa: {exc}") from exc
    finally:
        cursor.close()
        conn.close()

    return {"message": "Data siswa berhasil dihapus."}

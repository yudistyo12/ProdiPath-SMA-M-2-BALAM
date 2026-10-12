from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_db_connection
from backend.routes.auth import require_admin

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

SCORE_COLUMNS = [
    "nilai_matematika",
    "nilai_sains",
    "nilai_sosial",
    "nilai_bahasa",
]


@router.get("/summary", dependencies=[Depends(require_admin)])
def get_dashboard_summary():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Koneksi database gagal.")

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                SUM(sumber_data = 'dataset') AS total_siswa,
                SUM(sumber_data = 'kuesioner_web') AS total_pengisian_web
            FROM questionnaire_data
            """
        )
        totals = cursor.fetchone()
        total_siswa = totals["total_siswa"] or 0
        total_pengisian_web = totals["total_pengisian_web"] or 0

        cursor.execute(
            """
            SELECT rekomendasi_jurusan, COUNT(*) AS jumlah
            FROM questionnaire_data
            WHERE sumber_data = 'dataset'
            GROUP BY rekomendasi_jurusan
            ORDER BY jumlah DESC, rekomendasi_jurusan
            """
        )
        distribusi_rekomendasi = {
            row["rekomendasi_jurusan"]: row["jumlah"] for row in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT jurusan_sma, COUNT(*) AS jumlah
            FROM questionnaire_data
            WHERE sumber_data = 'dataset'
            GROUP BY jurusan_sma
            ORDER BY jurusan_sma
            """
        )
        distribusi_jurusan_sma = {
            row["jurusan_sma"]: row["jumlah"] for row in cursor.fetchall()
        }

        cursor.execute(
            "SELECT "
            + ", ".join(f"AVG({column}) AS {column}" for column in SCORE_COLUMNS)
            + " FROM questionnaire_data WHERE sumber_data = 'dataset'"
        )
        averages = cursor.fetchone()

        cursor.execute(
            """
            SELECT rekomendasi_jurusan, COUNT(*) AS jumlah
            FROM questionnaire_data
            WHERE sumber_data = 'kuesioner_web'
            GROUP BY rekomendasi_jurusan
            ORDER BY jumlah DESC, rekomendasi_jurusan
            """
        )
        distribusi_rekomendasi_web = {
            row["rekomendasi_jurusan"]: row["jumlah"] for row in cursor.fetchall()
        }

        cursor.execute(
            """
            SELECT jurusan_sma, COUNT(*) AS jumlah
            FROM questionnaire_data
            WHERE sumber_data = 'kuesioner_web'
            GROUP BY jurusan_sma
            ORDER BY jurusan_sma
            """
        )
        distribusi_jurusan_sma_web = {
            row["jurusan_sma"]: row["jumlah"] for row in cursor.fetchall()
        }

        cursor.execute(
            "SELECT "
            + ", ".join(f"AVG({column}) AS {column}" for column in SCORE_COLUMNS)
            + " FROM questionnaire_data WHERE sumber_data = 'kuesioner_web'"
        )
        averages_web = cursor.fetchone()

        return {
            "total_siswa": total_siswa,
            "total_pengisian_web": total_pengisian_web,
            "distribusi_rekomendasi": distribusi_rekomendasi,
            "distribusi_jurusan_sma": distribusi_jurusan_sma,
            "rata_rata_nilai": {
                column: round(float(averages[column] or 0), 1)
                for column in SCORE_COLUMNS
            },
            "distribusi_rekomendasi_web": distribusi_rekomendasi_web,
            "distribusi_jurusan_sma_web": distribusi_jurusan_sma_web,
            "rata_rata_nilai_web": {
                column: round(float(averages_web[column] or 0), 1)
                for column in SCORE_COLUMNS
            },
        }
    finally:
        cursor.close()
        conn.close()

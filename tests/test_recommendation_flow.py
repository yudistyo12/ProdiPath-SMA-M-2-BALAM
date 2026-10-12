import asyncio
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException, UploadFile

from backend.main import app
from backend.routes import dataset
from backend.routes.auth import create_access_token, require_admin
from backend.routes.predict import predict_major
from backend.schemas.models import PredictionRequest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class FakeCursor:
    def __init__(self):
        self.rows = []
        self.queries = []

    def execute(self, query, values):
        self.rows.append(values)
        self.queries.append(query)

    def close(self):
        pass


class FakeConnection:
    def __init__(self):
        self.fake_cursor = FakeCursor()
        self.committed = False

    def cursor(self):
        return self.fake_cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def close(self):
        pass


class RecommendationFlowTests(unittest.TestCase):
    def test_prediction_returns_a_known_major(self):
        request = PredictionRequest(
            nisn="0081234501",
            nama="Sendy Agus Priyanto",
            jurusan_sma="IPA",
            nilai_matematika=85,
            nilai_sains=88,
            nilai_sosial=75,
            nilai_bahasa=80,
            minat_teknologi=5,
            minat_seni=3,
            minat_komunikasi=3,
            kemampuan_analitis=5,
            persetujuan_data=True,
        )
        connection = FakeConnection()

        with patch("backend.routes.predict.get_db_connection", return_value=connection):
            result = predict_major(request)

        self.assertIsInstance(result["prediksi"], str)
        self.assertTrue(result["prediksi"])
        self.assertTrue(result["tersimpan"])
        self.assertEqual(result["nisn"], "0081234501")
        self.assertEqual(result["nama"], "Sendy Agus Priyanto")
        self.assertEqual(len(connection.fake_cursor.rows), 1)
        self.assertIn("'kuesioner_web'", connection.fake_cursor.queries[0])
        self.assertTrue(connection.fake_cursor.rows[0][-1])
        self.assertTrue(connection.committed)

    def test_prediction_requires_nisn_name_and_data_consent(self):
        with self.assertRaises(ValueError):
            PredictionRequest(
                nisn="123",
                nama="Siswa Contoh",
                jurusan_sma="IPA",
                nilai_matematika=80,
                nilai_sains=80,
                nilai_sosial=80,
                nilai_bahasa=80,
                minat_teknologi=3,
                minat_seni=3,
                minat_komunikasi=3,
                kemampuan_analitis=3,
                persetujuan_data=True,
            )

        with self.assertRaises(ValueError):
            PredictionRequest(
                nisn="0081234501",
                nama="Siswa Contoh",
                jurusan_sma="IPA",
                nilai_matematika=80,
                nilai_sains=80,
                nilai_sosial=80,
                nilai_bahasa=80,
                minat_teknologi=3,
                minat_seni=3,
                minat_komunikasi=3,
                kemampuan_analitis=3,
                persetujuan_data=False,
            )

    def test_import_accepts_the_project_dataset(self):
        connection = FakeConnection()
        csv_content = (PROJECT_ROOT / "data" / "questionnaire_real.csv").read_bytes()
        upload = UploadFile(
            filename="questionnaire_real.csv",
            file=BytesIO(csv_content),
        )

        with patch.object(dataset, "get_db_connection", return_value=connection):
            result = asyncio.run(dataset.import_dataset(upload))

        self.assertEqual(result["success_count"], 25)
        self.assertEqual(len(connection.fake_cursor.rows), 25)
        self.assertIn("'dataset'", connection.fake_cursor.queries[0])
        self.assertTrue(connection.committed)

    def test_import_reports_invalid_score_without_inserting_row(self):
        connection = FakeConnection()
        csv_content = (
            b"nisn,nama,jurusan_sma,nilai_matematika,nilai_sains,nilai_sosial,"
            b"nilai_bahasa,minat_teknologi,minat_seni,minat_komunikasi,"
            b"kemampuan_analitis,rekomendasi_jurusan\n"
            b"00001,Siswa Contoh,IPA,101,80,70,90,3,3,3,3,Teknik Informatika\n"
        )
        upload = UploadFile(filename="invalid.csv", file=BytesIO(csv_content))

        with patch.object(dataset, "get_db_connection", return_value=connection):
            result = asyncio.run(dataset.import_dataset(upload))

        self.assertEqual(result["success_count"], 0)
        self.assertEqual(connection.fake_cursor.rows, [])
        self.assertIn("Baris 2", result["errors"][0])

    def test_admin_guard_rejects_non_admin_tokens(self):
        token = create_access_token({"sub": "student", "role": "mahasiswa"})

        with self.assertRaises(HTTPException) as error:
            require_admin(token=token)

        self.assertEqual(error.exception.status_code, 403)

    def test_admin_data_routes_declare_bearer_authentication(self):
        schema = app.openapi()
        protected_paths = [
            "/api/dataset/import",
            "/api/students/",
            "/api/students/{nisn}",
            "/api/dashboard/summary",
            "/api/analysis/summary",
        ]

        for path in protected_paths:
            with self.subTest(path=path):
                operation = next(iter(schema["paths"][path].values()))
                self.assertIn("OAuth2PasswordBearer", operation["security"][0])


if __name__ == "__main__":
    unittest.main()

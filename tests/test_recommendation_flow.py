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
from backend.services.saw import rank_majors

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class FakeCursor:
    def __init__(self, reference_rows=None):
        self.rows = []
        self.queries = []
        self.reference_rows = reference_rows or []

    def execute(self, query, values=None):
        self.queries.append(query)
        if values is not None:
            self.rows.append(values)

    def fetchall(self):
        return self.reference_rows

    def close(self):
        pass


class FakeConnection:
    def __init__(self, reference_rows=None):
        self.fake_cursor = FakeCursor(reference_rows)
        self.committed = False

    def cursor(self, dictionary=False):
        return self.fake_cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def close(self):
        pass


class RecommendationFlowTests(unittest.TestCase):
    @staticmethod
    def reference_rows():
        return [
            {
                "jurusan_sma": "IPA",
                "nilai_matematika": 85,
                "nilai_sains": 88,
                "nilai_sosial": 75,
                "nilai_bahasa": 80,
                "minat_teknologi": 5,
                "minat_seni": 3,
                "minat_komunikasi": 3,
                "kemampuan_analitis": 5,
                "rekomendasi_jurusan": "Teknik Informatika",
            },
            {
                "jurusan_sma": "IPS",
                "nilai_matematika": 65,
                "nilai_sains": 60,
                "nilai_sosial": 90,
                "nilai_bahasa": 85,
                "minat_teknologi": 2,
                "minat_seni": 4,
                "minat_komunikasi": 5,
                "kemampuan_analitis": 3,
                "rekomendasi_jurusan": "Ilmu Komunikasi",
            },
        ]

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
        connection = FakeConnection(self.reference_rows())

        with patch("backend.routes.predict.get_db_connection", return_value=connection):
            result = predict_major(request)

        self.assertIsInstance(result["prediksi"], str)
        self.assertTrue(result["prediksi"])
        self.assertTrue(result["tersimpan"])
        self.assertEqual(result["nisn"], "0081234501")
        self.assertEqual(result["nama"], "Sendy Agus Priyanto")
        self.assertEqual(len(connection.fake_cursor.rows), 1)
        self.assertIn("WHERE sumber_data = 'dataset'", connection.fake_cursor.queries[0])
        self.assertIn("'kuesioner_web'", connection.fake_cursor.queries[1])
        self.assertTrue(connection.fake_cursor.rows[0][-1])
        self.assertTrue(connection.committed)
        self.assertEqual(result["metode"], "SAW")
        self.assertEqual(result["prediksi"], "Teknik Informatika")
        self.assertEqual(result["peringkat"][0]["jumlah_data"], 1)
        self.assertAlmostEqual(result["bobot_kriteria"], 1 / 9)

    def test_saw_ranks_closest_reference_profile_first(self):
        profile = self.reference_rows()[0]
        rankings = rank_majors(profile, self.reference_rows())

        self.assertEqual(rankings[0]["program_studi"], "Teknik Informatika")
        self.assertEqual(rankings[0]["skor"], 100.0)
        self.assertEqual(rankings[0]["jumlah_data"], 1)
        self.assertGreater(rankings[0]["skor"], rankings[1]["skor"])

    def test_saw_requires_reference_alternatives(self):
        with self.assertRaisesRegex(ValueError, "belum memiliki alternatif"):
            rank_majors(self.reference_rows()[0], [])

    def test_saw_calculates_all_criterion_scores_and_weighted_total(self):
        reference_rows = [
            {
                "jurusan_sma": "IPA",
                "nilai_matematika": 80,
                "nilai_sains": 80,
                "nilai_sosial": 80,
                "nilai_bahasa": 80,
                "minat_teknologi": 3,
                "minat_seni": 3,
                "minat_komunikasi": 3,
                "kemampuan_analitis": 3,
                "rekomendasi_jurusan": "Teknik Informatika",
            }
        ]
        profile = {
            "jurusan_sma": "IPA",
            "nilai_matematika": 100,
            "nilai_sains": 60,
            "nilai_sosial": 80,
            "nilai_bahasa": 80,
            "minat_teknologi": 5,
            "minat_seni": 1,
            "minat_komunikasi": 3,
            "kemampuan_analitis": 3,
        }

        ranking = rank_majors(profile, reference_rows)[0]

        details = ranking["rincian_kriteria"]
        self.assertEqual(details["jurusan_sma"], 100.0)
        self.assertEqual(details["nilai_matematika"], 80.0)
        self.assertEqual(details["nilai_sains"], 80.0)
        self.assertEqual(details["nilai_sosial"], 100.0)
        self.assertEqual(details["nilai_bahasa"], 100.0)
        self.assertEqual(details["minat_teknologi"], 50.0)
        self.assertEqual(details["minat_seni"], 50.0)
        self.assertEqual(details["minat_komunikasi"], 100.0)
        self.assertEqual(details["kemampuan_analitis"], 100.0)
        self.assertAlmostEqual(ranking["skor"], 84.44)

    def test_saw_track_match_uses_alternative_reference_percentage(self):
        reference_rows = [
            {
                "jurusan_sma": "IPA",
                "nilai_matematika": 80,
                "nilai_sains": 80,
                "nilai_sosial": 80,
                "nilai_bahasa": 80,
                "minat_teknologi": 3,
                "minat_seni": 3,
                "minat_komunikasi": 3,
                "kemampuan_analitis": 3,
                "rekomendasi_jurusan": "Teknik Informatika",
            },
            {
                "jurusan_sma": "IPS",
                "nilai_matematika": 80,
                "nilai_sains": 80,
                "nilai_sosial": 80,
                "nilai_bahasa": 80,
                "minat_teknologi": 3,
                "minat_seni": 3,
                "minat_komunikasi": 3,
                "kemampuan_analitis": 3,
                "rekomendasi_jurusan": "Teknik Informatika",
            },
        ]
        profile = dict(reference_rows[0])
        profile.pop("rekomendasi_jurusan")

        ranking = rank_majors(profile, reference_rows)[0]

        self.assertEqual(ranking["rincian_kriteria"]["jurusan_sma"], 50.0)
        self.assertEqual(ranking["jumlah_data"], 2)

    def test_saw_ties_alphabetically_by_program_name(self):
        base_row = self.reference_rows()[0]
        reference_rows = [
            dict(base_row, rekomendasi_jurusan="Zeta"),
            dict(base_row, rekomendasi_jurusan="Alpha"),
        ]

        rankings = rank_majors(self.reference_rows()[0], reference_rows)

        self.assertEqual(
            [item["program_studi"] for item in rankings],
            ["Alpha", "Zeta"],
        )

    def test_saw_rejects_missing_reference_column(self):
        reference_row = dict(self.reference_rows()[0])
        reference_row.pop("nilai_bahasa")

        with self.assertRaisesRegex(ValueError, "nilai_bahasa"):
            rank_majors(self.reference_rows()[0], [reference_row])

    def test_saw_rejects_invalid_reference_track(self):
        reference_row = dict(self.reference_rows()[0])
        reference_row["jurusan_sma"] = "Keagamaan"

        with self.assertRaisesRegex(ValueError, "baris 1 tidak valid"):
            rank_majors(self.reference_rows()[0], [reference_row])

    def test_saw_rejects_invalid_student_profile(self):
        profile = dict(self.reference_rows()[0])
        profile["jurusan_sma"] = "Keagamaan"

        with self.assertRaisesRegex(ValueError, "Profil siswa tidak valid"):
            rank_majors(profile, self.reference_rows())

        profile = dict(self.reference_rows()[0])
        profile.pop("nilai_matematika")

        with self.assertRaisesRegex(ValueError, "Profil siswa tidak lengkap"):
            rank_majors(profile, self.reference_rows())

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

from collections import defaultdict
from math import isfinite
from typing import Mapping, Sequence


TRACKS = {"IPA", "IPS", "Bahasa"}
NUMERIC_CRITERIA = (
    ("nilai_matematika", "Nilai Matematika", 100),
    ("nilai_sains", "Nilai Sains", 100),
    ("nilai_sosial", "Nilai Sosial", 100),
    ("nilai_bahasa", "Nilai Bahasa", 100),
    ("minat_teknologi", "Minat Teknologi", 4),
    ("minat_seni", "Minat Seni", 4),
    ("minat_komunikasi", "Minat Komunikasi", 4),
    ("kemampuan_analitis", "Kemampuan Analitis", 4),
)
CRITERIA = (("jurusan_sma", "Kesesuaian Peminatan SMA", 1),) + tuple(
    (field, label, maximum_difference)
    for field, label, maximum_difference in NUMERIC_CRITERIA
)
EQUAL_WEIGHT = 1 / len(CRITERIA)
REFERENCE_COLUMNS = (
    "jurusan_sma",
    *(field for field, _, _ in NUMERIC_CRITERIA),
    "rekomendasi_jurusan",
)


def rank_majors(
    profile: Mapping[str, object],
    reference_rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Rank study programs with SAW using normalized profile similarity scores."""
    grouped: dict[str, list[Mapping[str, object]]] = defaultdict(list)

    for row_number, row in enumerate(reference_rows, start=1):
        missing = [column for column in REFERENCE_COLUMNS if column not in row]
        if missing:
            raise ValueError(
                f"Data referensi baris {row_number} tidak memiliki kolom: "
                f"{', '.join(missing)}."
            )

        major = str(row["rekomendasi_jurusan"]).strip()
        track = str(row["jurusan_sma"]).strip()
        if not major or track not in TRACKS:
            raise ValueError(f"Data referensi baris {row_number} tidak valid.")

        for field, _, _ in NUMERIC_CRITERIA:
            try:
                value = float(row[field])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Nilai {field} pada data referensi baris {row_number} tidak valid."
                ) from exc
            if not isfinite(value):
                raise ValueError(
                    f"Nilai {field} pada data referensi baris {row_number} tidak valid."
                )
        grouped[major].append(row)

    if not grouped:
        raise ValueError("Dataset referensi belum memiliki alternatif program studi.")

    try:
        student_track = str(profile["jurusan_sma"]).strip()
        student_values = {
            field: float(profile[field]) for field, _, _ in NUMERIC_CRITERIA
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Profil siswa tidak lengkap untuk perhitungan SAW.") from exc

    if student_track not in TRACKS or not all(
        isfinite(value) for value in student_values.values()
    ):
        raise ValueError("Profil siswa tidak valid untuk perhitungan SAW.")

    rankings = []
    for major, rows in grouped.items():
        track_match = (
            sum(str(row["jurusan_sma"]).strip() == student_track for row in rows)
            / len(rows)
            * 100
        )
        criterion_scores = {"jurusan_sma": track_match}

        for field, _, maximum_difference in NUMERIC_CRITERIA:
            alternative_average = sum(float(row[field]) for row in rows) / len(rows)
            difference = abs(student_values[field] - alternative_average)
            criterion_scores[field] = max(
                0.0, (1 - difference / maximum_difference) * 100
            )

        total_score = sum(
            criterion_scores[field] * EQUAL_WEIGHT for field, _, _ in CRITERIA
        )
        rankings.append(
            {
                "program_studi": major,
                "skor": round(total_score, 2),
                "jumlah_data": len(rows),
                "rincian_kriteria": {
                    field: round(criterion_scores[field], 2)
                    for field, _, _ in CRITERIA
                },
            }
        )

    return sorted(
        rankings,
        key=lambda item: (-float(item["skor"]), str(item["program_studi"]).casefold()),
    )

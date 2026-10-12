import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

NUMERIC_FEATURES = [
    "nilai_matematika",
    "nilai_sains",
    "nilai_sosial",
    "nilai_bahasa",
    "minat_teknologi",
    "minat_seni",
    "minat_komunikasi",
    "kemampuan_analitis",
]
CATEGORICAL_FEATURES = ["jurusan_sma"]
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET = "rekomendasi_jurusan"


def prepare_data(df: pd.DataFrame):
    """Validate the recommendation dataset and encode its target labels."""
    missing_columns = [column for column in FEATURES + [TARGET] if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Kolom dataset tidak ditemukan: {', '.join(missing_columns)}")

    df = df.dropna(subset=FEATURES + [TARGET]).copy()
    if df.empty:
        raise ValueError("Dataset tidak memiliki baris lengkap untuk melatih model.")

    X = df[FEATURES].copy()
    X["jurusan_sma"] = X["jurusan_sma"].astype(str).str.strip()
    y = df[TARGET].astype(str).str.strip()
    if (X["jurusan_sma"] == "").any() or (y == "").any():
        raise ValueError("Kolom jurusan_sma dan rekomendasi_jurusan tidak boleh kosong.")

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    return X, y_encoded, label_encoder


def make_track_encoder():
    """Create a compatible encoder for the high-school track feature."""
    return OneHotEncoder(handle_unknown="ignore")

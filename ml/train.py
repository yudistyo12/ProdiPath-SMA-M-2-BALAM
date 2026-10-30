import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

from preprocessing import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    make_track_encoder,
    prepare_data,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def train_model(data_path=None, models_dir=None):
    dataset_path = Path(data_path) if data_path else PROJECT_ROOT / "data" / "questionnaire_real.csv"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset tidak ditemukan: {dataset_path}")

    df = pd.read_csv(dataset_path)
    X, y, label_encoder = prepare_data(df)

    if len(set(y)) < 2:
        raise ValueError("Dataset harus memiliki setidaknya dua kelas jurusan.")

    if len(X) >= 5:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        evaluation_model = make_model()
        evaluation_model.fit(X_train, y_train)
        y_pred = evaluation_model.predict(X_test)
        print(
            "Akurasi pemeriksaan holdout "
            f"(bukan jaminan akurasi di dunia nyata): {accuracy_score(y_test, y_pred):.2f}"
        )

    model = make_model()
    model.fit(X, y)

    output_dir = Path(models_dir) if models_dir else PROJECT_ROOT / "models"
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model_jurusan.pkl"
    encoder_path = output_dir / "label_encoder.pkl"
    joblib.dump(model, model_path)
    joblib.dump(label_encoder, encoder_path)
    print(
        f"Model rekomendasi dilatih dengan {len(X)} data dari {dataset_path} "
        f"dan disimpan di {model_path}"
    )


def make_model():
    preprocessor = ColumnTransformer(
        transformers=[
            ("jurusan_sma", make_track_encoder(), CATEGORICAL_FEATURES),
            ("nilai_dan_minat", "passthrough", NUMERIC_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", DecisionTreeClassifier(random_state=42, max_depth=5)),
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Latih model rekomendasi jurusan.")
    parser.add_argument(
        "--data",
        type=Path,
        default=PROJECT_ROOT / "data" / "questionnaire_real.csv",
        help="Lokasi CSV untuk pelatihan.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "models",
        help="Folder penyimpanan model dan encoder hasil pelatihan.",
    )
    args = parser.parse_args()
    train_model(data_path=args.data, models_dir=args.output_dir)

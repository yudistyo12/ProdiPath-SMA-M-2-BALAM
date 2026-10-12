import os

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


def train_model():
    data_path = os.path.join(os.path.dirname(__file__), "../data/questionnaire_real.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset tidak ditemukan: {data_path}")

    df = pd.read_csv(data_path)
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
            "Akurasi evaluasi holdout "
            f"(indikatif untuk dataset kecil): {accuracy_score(y_test, y_pred):.2f}"
        )

    model = make_model()
    model.fit(X, y)

    models_dir = os.path.join(os.path.dirname(__file__), "../models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, "model_jurusan.pkl")
    encoder_path = os.path.join(models_dir, "label_encoder.pkl")
    joblib.dump(model, model_path)
    joblib.dump(label_encoder, encoder_path)
    print(f"Model rekomendasi jurusan dilatih dengan {len(X)} data dan disimpan di {model_path}")


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
    train_model()

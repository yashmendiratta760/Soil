import pickle
from contextlib import asynccontextmanager
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import PredictionRequest, PredictionResponse

MODEL_PATH = Path(__file__).parent / "model" / "fertilizer_xgb_model.pkl"

# ---------------------------------------------------------------------------
# IMPORTANT: the model's classes_ are numeric-encoded (0-6), produced by a
# sklearn LabelEncoder on the fertilizer name column during training. This is
# the label order LabelEncoder produces for the standard Kaggle "Fertilizer
# Prediction" dataset's 7 classes (alphabetical order). If your training
# notebook printed a different `label_encoder.classes_`, replace this list
# with that exact order — position i here MUST correspond to encoded class i.
# ---------------------------------------------------------------------------
FERTILIZER_LABELS = [
    "10-26-26",
    "14-35-14",
    "17-17-17",
    "20-20",
    "28-28",
    "DAP",
    "Urea",
]

model = None
FEATURE_COLUMNS: list[str] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, FEATURE_COLUMNS
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found at {MODEL_PATH}")
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    FEATURE_COLUMNS = list(model.feature_names_in_)
    yield
    model = None


app = FastAPI(
    title="Fertilizer Recommendation API",
    description="Predicts the recommended fertilizer based on soil, weather, and crop data.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_feature_row(payload: PredictionRequest) -> pd.DataFrame:
    """Convert the user-facing request into the exact one-hot encoded
    22-column row the model was trained on."""
    row = {col: 0.0 for col in FEATURE_COLUMNS}

    row["Temparature"] = payload.temperature  # matches training column's spelling
    row["Humidity"] = payload.humidity
    row["Moisture"] = payload.moisture
    row["Nitrogen"] = payload.nitrogen
    row["Potassium"] = payload.potassium
    row["Phosphorous"] = payload.phosphorous

    soil_col = f"Soil Type_{payload.soil_type.value}"
    crop_col = f"Crop Type_{payload.crop_type.value}"

    if soil_col not in row:
        raise HTTPException(status_code=400, detail=f"Unknown soil type column: {soil_col}")
    if crop_col not in row:
        raise HTTPException(status_code=400, detail=f"Unknown crop type column: {crop_col}")

    row[soil_col] = 1.0
    row[crop_col] = 1.0

    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


@app.get("/")
def root():
    return {"status": "ok", "message": "Fertilizer Recommendation API is running."}


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None}


@app.get("/metadata")
def metadata():
    return {
        "n_features": len(FEATURE_COLUMNS),
        "feature_columns": FEATURE_COLUMNS,
        "fertilizer_labels": FERTILIZER_LABELS,
        "n_classes": len(FERTILIZER_LABELS),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    features = build_feature_row(payload)

    try:
        pred_class = int(model.predict(features)[0])
        proba = model.predict_proba(features)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    if pred_class >= len(FERTILIZER_LABELS):
        raise HTTPException(
            status_code=500,
            detail="Predicted class index has no matching label in FERTILIZER_LABELS.",
        )

    probabilities = {
        FERTILIZER_LABELS[i]: round(float(p), 4) for i, p in enumerate(proba)
    }

    return PredictionResponse(
        fertilizer=FERTILIZER_LABELS[pred_class],
        fertilizer_code=pred_class,
        confidence=round(float(proba[pred_class]), 4),
        probabilities=probabilities,
    )

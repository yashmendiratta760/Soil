# Fertilizer Recommendation API

FastAPI backend serving the `fertilizer_xgb_model.pkl` XGBoost classifier.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs: http://localhost:8000/docs

## Endpoints

| Method | Path        | Description                                  |
|--------|-------------|-----------------------------------------------|
| GET    | `/`         | Health/status check                          |
| GET    | `/health`   | Confirms the model is loaded                 |
| GET    | `/metadata` | Feature columns, class labels, model info    |
| POST   | `/predict`  | Predict recommended fertilizer               |

### `POST /predict`

Request body:
```json
{
  "temperature": 26,
  "humidity": 52,
  "moisture": 38,
  "nitrogen": 37,
  "potassium": 0,
  "phosphorous": 0,
  "soil_type": "Sandy",
  "crop_type": "Maize"
}
```

`soil_type` must be one of: `Black`, `Clayey`, `Loamy`, `Red`, `Sandy`
`crop_type` must be one of: `Barley`, `Cotton`, `Ground Nuts`, `Maize`, `Millets`, `Oil seeds`, `Paddy`, `Pulses`, `Sugarcane`, `Tobacco`, `Wheat`

(These match the exact one-hot columns the model was trained on — anything else is rejected with a 422.)

Response:
```json
{
  "fertilizer": "17-17-17",
  "fertilizer_code": 2,
  "confidence": 0.2099,
  "probabilities": {
    "10-26-26": 0.161,
    "14-35-14": 0.1217,
    "17-17-17": 0.2099,
    "20-20": 0.1336,
    "28-28": 0.1107,
    "DAP": 0.1519,
    "Urea": 0.1112
  }
}
```

## ⚠️ Important: verify the fertilizer label mapping

The model's `classes_` are numeric codes (`0`–`6`) produced by a `LabelEncoder`
fit on the fertilizer name column during training — the `.pkl` file does **not**
store that encoder or the original string labels.

In `app/main.py`, `FERTILIZER_LABELS` is currently set to the alphabetical
order sklearn's `LabelEncoder` would normally produce for the standard 7-class
fertilizer dataset:

```python
FERTILIZER_LABELS = ["10-26-26", "14-35-14", "17-17-17", "20-20", "28-28", "DAP", "Urea"]
```

**Please confirm this against your training notebook** (e.g. by printing
`label_encoder.classes_` there) and edit this list if the order differs —
position `i` in the list must match encoded class `i`. Everything else in the
API works correctly regardless; only the human-readable names at the end
depend on this list.

## Project structure

```
fertilizer_api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, model loading, /predict logic
│   ├── schemas.py        # Pydantic request/response models + enums
│   └── model/
│       └── fertilizer_xgb_model.pkl
├── requirements.txt
└── README.md
```

## Streamlit frontend

A simple UI (`streamlit_app.py`) is included that calls the FastAPI `/predict`
endpoint and displays **only the recommended fertilizer name**.

1. Make sure the FastAPI backend is already running (see "Run" above) at
   `http://localhost:8000`.
2. In a **separate terminal** (same venv), run:
   ```bash
   streamlit run streamlit_app.py
   ```
3. It opens automatically at `http://localhost:8501`. Fill in the form and
   click "Predict Fertilizer" — the result shows just the fertilizer name,
   e.g. **Recommended Fertilizer: 17-17-17**.

If your API runs on a different host/port, update `API_URL` at the top of
`streamlit_app.py`.

## Docker (optional)

```dockerfile
FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

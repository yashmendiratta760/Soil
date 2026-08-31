from enum import Enum

from pydantic import BaseModel, Field


class SoilType(str, Enum):
    black = "Black"
    clayey = "Clayey"
    loamy = "Loamy"
    red = "Red"
    sandy = "Sandy"


class CropType(str, Enum):
    barley = "Barley"
    cotton = "Cotton"
    ground_nuts = "Ground Nuts"
    maize = "Maize"
    millets = "Millets"
    oil_seeds = "Oil seeds"
    paddy = "Paddy"
    pulses = "Pulses"
    sugarcane = "Sugarcane"
    tobacco = "Tobacco"
    wheat = "Wheat"


class PredictionRequest(BaseModel):
    temperature: float = Field(..., ge=-10, le=60, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    moisture: float = Field(..., ge=0, le=100, description="Soil moisture (%)")
    nitrogen: float = Field(..., ge=0, le=200, description="Nitrogen content in soil")
    potassium: float = Field(..., ge=0, le=200, description="Potassium content in soil")
    phosphorous: float = Field(..., ge=0, le=200, description="Phosphorous content in soil")
    soil_type: SoilType
    crop_type: CropType

    model_config = {
        "json_schema_extra": {
            "example": {
                "temperature": 26,
                "humidity": 52,
                "moisture": 38,
                "nitrogen": 37,
                "potassium": 0,
                "phosphorous": 0,
                "soil_type": "Sandy",
                "crop_type": "Maize",
            }
        }
    }


class PredictionResponse(BaseModel):
    fertilizer: str
    fertilizer_code: int
    confidence: float
    probabilities: dict[str, float]

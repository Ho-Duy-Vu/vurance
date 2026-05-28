from datetime import datetime
from typing import Literal

from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING


class DisasterRisk(BaseModel):
    type: Literal["storm", "flood", "landslide", "inundation", "drought"]
    risk_score: int
    frequency: Literal["high", "medium", "low"]
    historical_events: int


class InsuranceRecommendation(BaseModel):
    insurance_type: str
    priority_score: int
    reason: str


class GeoRisk(Document):
    province_name: str
    province_code: str
    region: Literal["north", "central", "south"]
    overall_risk_score: int

    disaster_risks: list[DisasterRisk] = []
    recommendations: list[InsuranceRecommendation] = []

    is_high_risk: bool = False
    risk_factors: list[str] = []

    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "geo_risks"
        indexes = [
            IndexModel([("province_name", ASCENDING)]),
            IndexModel([("province_code", ASCENDING)]),
            IndexModel([("region", ASCENDING)]),
            IndexModel([("is_high_risk", ASCENDING)]),
        ]

# app/schemas.py
from datetime import date
from typing import List

from pydantic import BaseModel, Field


class PlanActivityRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    date: date  # aceita string "YYYY-MM-DD" e converte pra date


class PlanActivityResponse(BaseModel):
    sunrise: str
    sunset: str
    day_length: str
    activities: List[str]
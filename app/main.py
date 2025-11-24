# app/main.py
from datetime import date

import httpx
from fastapi import FastAPI, HTTPException

from .schemas import PlanActivityRequest, PlanActivityResponse
from .utils import SUNRISE_API_URL, TIMEZONE, strip_seconds

app = FastAPI(title="Outdoor Activity Planner")

def strip_seconds(time_str: str) -> str:
    # Remove os segundos de uma string de horário no formato 'H:MM:SS AM/PM'
    # Ex: '2:08:55 PM' -> '2:08 PM'
    # Se o formato for inesperado, devolve a string original.

    if not isinstance(time_str, str):
        return time_str

    parts = time_str.split()
    if len(parts) != 2:
        return time_str

    time_part, ampm = parts  # ex: "2:08:55", "PM"
    subparts = time_part.split(":")
    if len(subparts) < 2:
        return time_str

    # Pega só horas e minutos
    hh_mm = ":".join(subparts[:2])  # "2:08"
    return f"{hh_mm} {ampm}"

@app.get("/")
def root():
    return {
        "message": "API de planejamento de atividades ao ar livre. Use POST /plan-activity."
    }

async def fetch_sun_data(   # Consulta a API Sunrise-Sunset e retorna o dict 'results'
    latitude: float,        # com sunrise, sunset, day_length, etc.
    longitude: float,
    target_date: date,
) -> dict:
    params = {
        "lat": latitude,
        "lng": longitude,
        "date": target_date.isoformat(),  # "YYYY-MM-DD"
        "tzid": TIMEZONE,
        "formatted": 1,  # deixa a API já devolver em formato "7:45:32 AM"
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(SUNRISE_API_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            # Erro de rede, timeout, etc.
            raise HTTPException(
                status_code=502,
                detail="Erro ao consultar serviço externo de nascer/pôr do sol.",
            ) from exc

    data = response.json()

    if data.get("status") != "OK":
        # A API respondeu, mas com erro de domínio (ex: lat/long inválidos, etc.)
        raise HTTPException(
            status_code=502,
            detail=f"Serviço externo retornou status '{data.get('status')}'.",
        )

    # Esperamos que exista a chave "results"
    results = data.get("results")
    if not results:
        raise HTTPException(
            status_code=502,
            detail="Resposta do serviço externo não contém dados esperados.",
        )

    return results

@app.post("/plan-activity", response_model=PlanActivityResponse)
async def plan_activity(payload: PlanActivityRequest) -> PlanActivityResponse:

    # Rota principal do desafio.
    # - Consulta a API Sunrise-Sunset
    # - Monta as atividades dinamicamente
    # - Devolve sunrise, sunset, day_length e lista de atividades

    sun_data = await fetch_sun_data(
        latitude=payload.latitude,
        longitude=payload.longitude,
        target_date=payload.date,
    )

    sunrise = sun_data.get("sunrise")
    sunset = sun_data.get("sunset")
    day_length = sun_data.get("day_length")

    if not (sunrise and sunset and day_length):
        raise HTTPException(
            status_code=502,
            detail="Dados incompletos retornados pelo serviço externo.",
        )

    sunrise_short = strip_seconds(sunrise)
    sunset_short = strip_seconds(sunset)

    activities = [
        f"Caminhada ao nascer do sol às {sunrise_short}",
        "Piquenique durante o dia",
        f"Fotografia ao pôr do sol às {sunset_short}",
        "Observação de estrelas após o pôr do sol",
    ]

    return PlanActivityResponse(
        sunrise=sunrise,
        sunset=sunset,
        day_length=day_length,
        activities=activities,
    )
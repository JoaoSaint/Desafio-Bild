import logging
import asyncio
from datetime import date
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from .schemas import PlanActivityRequest, PlanActivityResponse
from .utils import SUNRISE_API_URL, TIMEZONE, strip_seconds

logger = logging.getLogger("app")

if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    )

app = FastAPI(title="Outdoor Activity Planner")

app.mount(
    "/frontend",
    StaticFiles(directory="frontend", html=True),
    name="frontend",
)

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

@app.get("/", include_in_schema=False)
def root():
    # Quando alguém acessa "/", manda direto pro frontend
    return RedirectResponse(url="/frontend")

async def fetch_sun_data(   # Consulta a API Sunrise-Sunset e retorna o dict 'results' com sunrise,
    latitude: float,        # sunset, day_length, etc.
    longitude: float,       # Conta com até 3 tentativas no total (1 tentativa +2 retries)
    target_date: date,
) -> dict:

    params = {
        "lat": latitude,
        "lng": longitude,
        "date": target_date.isoformat(),  # "YYYY-MM-DD"
        "tzid": TIMEZONE,
        "formatted": 1,
    }

    max_attempts = 3
    delay = 1.0  # segundos

    async with httpx.AsyncClient(timeout=10.0) as client:
        last_exc: Exception | None = None

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(
                    "Chamando Sunrise-Sunset API (tentativa %d/%d) lat=%s lng=%s date=%s",
                    attempt,
                    max_attempts,
                    latitude,
                    longitude,
                    target_date.isoformat(),
                )

                response = await client.get(SUNRISE_API_URL, params=params)
                response.raise_for_status()

                data = response.json()

                if data.get("status") != "OK":
                    # Erro de domínio da API (ex.: parâmetros inválidos)
                    logger.error(
                        "Sunrise-Sunset retornou status '%s' na tentativa %d: %s",
                        data.get("status"),
                        attempt,
                        data,
                    )

                    raise HTTPException(
                        status_code=502,
                        detail=f"Serviço externo retornou status '{data.get('status')}'.",
                    )

                results = data.get("results")
                if not results:
                    logger.error(
                        "Sunrise-Sunset retornou payload sem 'results' na tentativa %d: %s",
                        attempt,
                        data,
                    )
                    raise HTTPException(
                        status_code=502,
                        detail="Resposta do serviço externo não contém dados esperados.",
                    )

                # Sucesso: retorna os dados
                logger.info("Sunrise-Sunset OK na tentativa %d", attempt)
                return results

            except httpx.HTTPError as exc:
                # Timeout, erro de conexão, etc.
                last_exc = exc
                logger.warning(
                    "Erro HTTP ao chamar Sunrise-Sunset na tentativa %d/%d: %s",
                    attempt,
                    max_attempts,
                    repr(exc),
                )

                if attempt < max_attempts:
                    logger.info("Aguardando %.1fs antes do retry...", delay)
                    await asyncio.sleep(delay)
                    delay *= 2  # backoff exponencial (1s -> 2s)
                else:
                    logger.exception(
                        "Falha definitiva ao chamar Sunrise-Sunset após %d tentativas",
                        max_attempts,
                    )

        # Se chegou aqui, todas as tentativas falharam por erro HTTP
        raise HTTPException(
            status_code=502,
            detail="Erro ao consultar serviço externo de nascer/pôr do sol após múltiplas tentativas.",
        ) from last_exc

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
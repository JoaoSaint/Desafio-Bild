SUNRISE_API_URL = "https://api.sunrise-sunset.org/json"
TIMEZONE = "America/Sao_Paulo"


def strip_seconds(time_str: str) -> str:
    """
    Remove os segundos de uma string de horário no formato 'H:MM:SS AM/PM'
    Ex: '2:08:55 PM' -> '2:08 PM'
    Se o formato for inesperado, devolve a string original.
    """
    if not isinstance(time_str, str):
        return time_str

    parts = time_str.split()
    if len(parts) != 2:
        return time_str

    time_part, ampm = parts  # ex: "2:08:55", "PM"
    subparts = time_part.split(":")
    if len(subparts) < 2:
        return time_str

    hh_mm = ":".join(subparts[:2])  # "2:08"
    return f"{hh_mm} {ampm}"

from domain import WeatherSnap


def classify_weather(weather: WeatherSnap) -> int:
    """
    Преобразует WeatherSnap в уровени 1–4.
    4 — очень холодно
    3 — холодно
    2 — средне
    1 — жарко
    """
    avg_temp = (weather.morning_temp + weather.day_temp
                + weather.evening_temp) / 3

    if avg_temp <= -5:
        return 4   # very cold
    elif avg_temp <= 5:
        return 3   # cold
    elif avg_temp <= 18:
        return 2   # mild
    else:
        return 1   # hot

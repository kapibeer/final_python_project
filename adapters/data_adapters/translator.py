import requests


def translate(text: str, source: str = "en", target: str = "ru") -> str:
    if not text.strip():
        return text

    try:
        response = requests.post(
            "https://libretranslate.de/translate",
            json={
                "q": text,
                "source": source,
                "target": target,
                "format": "text",
            },
            timeout=3,
        )

        if response.status_code != 200:
            return text

        data = response.json()
        translated = data.get("translatedText")

        if not translated:
            return text

        return translated

    except Exception:
        return text

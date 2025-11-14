import json  # noqa: F401
from modulok.config import BASE_DIR  # noqa: F401

JSON_PATH = BASE_DIR / "static" / "mentett_adatok.json"


def load_data():
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Hiba mentéskor: {e}")
        return False


def export_horoscope(data: dict, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def load_horoscope(filename: str) -> dict:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

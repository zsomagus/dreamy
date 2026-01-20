import os, json

def load_alomszotar(filepath: str = None):
    """Betölti az álomszótár JSON fájlt."""
    if filepath is None:
        # alapértelmezett: a projekt gyökerében lévő alomszotar.json
        filepath = os.path.join(os.path.dirname(__file__), "..", "alomszotar.json")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Hiba: alomszotar.json nem található.")
        return {}
    except json.JSONDecodeError:
        print("Hiba: alomszotar.json sérült.")
        return {}

# Példa: keresés egy kulcsszóra
def keres_alomjelentes(kulcsszo: str, data: dict):
    for item in data.get("alomszotar", []):
        if item["kulcsszo"] == kulcsszo:
            return item["jelentesek"]
    return ["Nincs találat az álomszótárban."]


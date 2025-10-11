import json
from static import yantra_analysis
def load_yantra_analysis(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_yantra_info_by_tithi(tithi, data):
    for yantra in data:
        if yantra["tithi"] == tithi:
            return yantra
    return None

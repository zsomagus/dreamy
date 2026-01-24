import logging
import re
from pathlib import Path
import pandas as pd
import swisseph as swe
import os
import pandas as pd
from countryinfo import CountryInfo
import pendulum  # ⏳ új: pendulum a datetime helyett
# Alap elérési utak
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

YANTRA_PATH = STATIC_DIR / "yantra"

# Swiss Ephemeris elérési út
swe.set_ephe_path(str(STATIC_DIR / "ephe"))

# Névmezők (külső modulok állítsák be futás közben)
aktualis_vezeteknev = ""
aktualis_keresztnev = ""

koord1_file = os.path.join(os.path.dirname(__file__), "static", "file1.xlsx")
koord2_file = os.path.join(os.path.dirname(__file__), "static", "file2.xlsx")


def get_coordinates(city_name: str, file1: str, file2: str):
    for file in [file1, file2]:
        if os.path.exists(file):
            df = pd.read_excel(file)
            df["name_lower"] = df["name"].str.lower()
            row = df[df["name_lower"] == city_name.lower()]
            if not row.empty:
                return float(row["lat"].iloc[0]), float(row["lon"].iloc[0])
    return None, None


def fill_coordinate_entries(city_name: str, lat_entry, lon_entry) -> bool:
    lat, lon = None, None

    # 1️⃣ CountryInfo
    try:
        ci = CountryInfo(city_name)
        info = ci.info()
        if "latlng" in info and info["latlng"]:
            lat, lon = info["latlng"][0], info["latlng"][1]
    except Exception:
        pass

    # 2️⃣ Excel fallback
    if lat is None or lon is None:
        base = os.path.dirname(__file__)
        file1 = os.path.join(base, "static", "file1.xlsx")
        file2 = os.path.join(base, "static", "file2.xlsx")
        lat, lon = get_coordinates(city_name, file1, file2)

    # 3️⃣ GUI mezők kitöltése
    if lat is not None and lon is not None:
        lat_entry.setText(str(lat))
        lon_entry.setText(str(lon))
        return True

    return False

import logging
import re
from pathlib import Path
import pandas as pd
import swisseph as swe
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

def fill_coordinate_entries(city_name: str, lat_entry, lon_entry) -> bool:
    """
    Koordináták kitöltése GUI Entry mezőkbe.
    Első: countryinfo (ország), ha nincs → Excel fájl.
    """
    lat, lon = None, None

    # 1️⃣ CountryInfo próbálkozás
    try:
        ci = countryinfo.CountryInfo(city_name)
        info = ci.info()
        if "latlng" in info and info["latlng"]:
            lat, lon = info["latlng"][0], info["latlng"][1]
    except Exception as e:
        logger.debug(f"CountryInfo nem talált adatot: {e}")

    # 2️⃣ Ha nincs találat → Excel fallback
    if lat is None or lon is None:
        lat, lon = get_coordinates(city_name, koord1_file, koord2_file)

    # 3️⃣ GUI mezők feltöltése
    if lat is not None and lon is not None:
        lat_entry.delete(0, "end")
        lat_entry.insert(0, str(lat))
        lon_entry.delete(0, "end")
        lon_entry.insert(0, str(lon))
        return True

    return False

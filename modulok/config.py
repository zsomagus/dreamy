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
YANTRA_DIR = STATIC_DIR / "yantrák"
HANG_DIR = STATIC_DIR / "hangok"
YANTRA_PATH = STATIC_DIR / "yantra"

# Swiss Ephemeris elérési út
swe.set_ephe_path(str(STATIC_DIR / "ephe"))

# Névmezők (külső modulok állítsák be futás közben)
aktualis_vezeteknev = ""
aktualis_keresztnev = ""

# Mentési/forrás fájlok
peoples_data_file = "mentett_adatok.json"
excel_file = "asztrológiai_adatbázis.xlsx"
koord1_file = "file1.xlsx"
koord2_file = "file2.xlsx"

excel_path = BASE_DIR / "static" / "asztrológiai_adatbázis.xlsx"
jegyek_df = pd.read_excel(excel_path, sheet_name="Jegyek")
hazak_df = pd.read_excel(excel_path, sheet_name="Házak")
bolygok_df = pd.read_excel(excel_path, sheet_name="Bolygók")
nakshatra_df = pd.read_excel(excel_path, sheet_name="Nakshatra _ Pada")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Konfigurációs szótár
config_dict = {
    "json_path": STATIC_DIR / "mentett_adatok.json",
    "mantra_dir": STATIC_DIR / "mantrák",
    "ambiance_path": STATIC_DIR / "hangok" / "ambiance.wav",
    "harang_path": STATIC_DIR / "hangok" / "templom harang.wav",
    "galboro_path": STATIC_DIR / "hangok" / "galboro.wav",
    "zaj_path": STATIC_DIR / "hangok" / "zaj.wav",
    "YANTRA_PATH": YANTRA_PATH,
}

def init_settings() -> None:
    """Alap beállítások kiírása (debug)."""
    print("Beállítások inicializálva:")
    print("YANTRA_DIR:", YANTRA_DIR)
    print("HANG_DIR:", HANG_DIR)

# -----------------------------
# Koordináta kereső utilok
# -----------------------------

def get_coordinates(
    city_name: str, file1: str | Path = koord1_file, file2: str | Path = koord2_file
) -> tuple[float | None, float | None]:
    """
    Városnév alapján koordináták keresése két Excel fájlban.
    """
    try:
        df1 = pd.read_excel(file1)
        df2 = pd.read_excel(file2)
        df = pd.concat([df1, df2], ignore_index=True)

        city_name_lower = city_name.strip().lower()
        match = df[df["City"].str.lower() == city_name_lower]

        if match.empty:
            match = df[df["City"].str.lower().str.contains(city_name_lower)]

        if not match.empty:
            lat = match.iloc[0]["Latitude"]
            lon = match.iloc[0]["Longitude"]
            return convert_coordinate_format(lat), convert_coordinate_format(lon)

    except Exception as e:
        logger.exception(f"Hiba a koordináta-keresés során: {e}")

    return None, None


def convert_coordinate_format(coord) -> float | None:
    """Koordináta konvertálása decimális fokra."""
    try:
        if isinstance(coord, (int, float)):
            return float(coord)

        coord_str = str(coord).strip().replace(",", ".")
        if re.match(r"^-?\d+\.\d+$", coord_str):
            return float(coord_str)

        dms_pattern = r"(\d+)[°º]\s*(\d+)[\'′]?\s*(\d+)?[\"″]?\s*([NSEW])"
        match = re.match(dms_pattern, coord_str)
        if match:
            deg = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3)) if match.group(3) else 0
            direction = match.group(4).upper()
            decimal = deg + minutes / 60 + seconds / 3600
            if direction in ["S", "W"]:
                decimal *= -1
            return decimal

        simple_pattern = r"(\d+)\s+(\d+)\s+([NSEW])"
        match = re.match(simple_pattern, coord_str)
        if match:
            deg = int(match.group(1))
            minutes = int(match.group(2))
            direction = match.group(3).upper()
            decimal = deg + minutes / 60
            if direction in ["S", "W"]:
                decimal *= -1
            return decimal

        numeric = re.sub(r"[^\d\.-]", "", coord_str)
        return float(numeric)

    except Exception:
        return None

# -----------------------------
# Időzóna / UTC utilok Pendulum-mal
# -----------------------------

def convert_to_utc(date_str: str, time_str: str, tz_str: str) -> pendulum.DateTime:
    """
    Helyi idő + időzóna → UTC (pendulum).
    """
    try:
        dt = pendulum.from_format(f"{date_str} {time_str}", "YYYY-MM-DD HH:mm", tz=tz_str)
        return dt.in_timezone("UTC")
    except Exception as e:
        logger.error(f"Hiba UTC konverziónál: {e}")
        raise

def is_dst_active(dt: pendulum.DateTime, timezone_str: str) -> bool:
    tz = pendulum.timezone(timezone_str)
    localized = dt.in_timezone(tz)
    return localized.dst().total_seconds() > 0

# -----------------------------
# GUI helper függvények
# -----------------------------

def update_utc_field_from_gui(date_entry, time_entry, tz_entry, utc_entry) -> None:
    """GUI mezőkből frissíti a UTC mezőt."""
    date_input = (date_entry.get() or "").strip()
    time_input = (time_entry.get() or "").strip()
    tz_input = (tz_entry.get() or "").strip()
    if not (date_input and time_input and tz_input):
        return
    try:
        utc_dt = convert_to_utc(date_input, time_input, tz_input)
        utc_entry.delete(0, "end")
        utc_entry.insert(0, utc_dt.to_datetime_string())
    except Exception:
        return

def set_dst_flag(var, timezone_str: str = "Europe/Budapest", dt: pendulum.DateTime | None = None) -> None:
    """Nyári időszámítás állapot beállítása GUI változóra."""
    dt = dt or pendulum.now()
    var.set(is_dst_active(dt, timezone_str))

def search_coordinates(city_name: str, lat_var, lon_var) -> bool:
    """Excel alapú koordináta keresés GUI változókba."""
    lat, lon = get_coordinates(city_name, koord1_file, koord2_file)
    if lat is not None and lon is not None:
        lat_var.set(lat)
        lon_var.set(lon)
        return True
    return False

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

import os
import swisseph as swe
import pendulum  # ⏳ datetime+pytz helyett
from modulok.config import YANTRA_PATH
from modulok.tables import varga_factors

# 🌌 Teljes bolygóadatok lekérése, Rahu–Ketu-val és házakkal
# 🧼 Értékek tisztítása

# 🧭 Ayanamsa lekérése
def get_ayanamsa(jd):
    return swe.get_ayanamsa_ut(jd)

def sanitize_number(value) -> float | None:
    try:
        if isinstance(value, (tuple, list)) and len(value) > 0:
            value = value[0]
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
        return float(value)
    except (ValueError, TypeError):
        return None

def sanitize_longitude(value) -> float:
    num = sanitize_number(value)
    return num % 360 if num is not None else 0.0

# 🌌 Nakshatra és pada számítása
def calculate_nakshatra(longitude, ayanamsa, nakshatras):
    sidereal_longitude = (longitude - ayanamsa) % 360
    nakshatra_index = int(sidereal_longitude // 13.3333) % 27
    nakshatra = nakshatras[nakshatra_index]
    pada = int((sidereal_longitude % 13.3333) // 3.3333) + 1
    return nakshatra, pada

# 🧘 Yantra fájl keresése tithi alapján
def find_yantra_by_tithi(tithi, yantra_folder=YANTRA_PATH):
    for fname in os.listdir(yantra_folder):
        if fname.lower().endswith(".jpg") and fname.startswith(str(tithi)):
            return os.path.join(yantra_folder, fname)
    return None

# 🧮 Varga pozíciók számítása
def calculate_varga_positions(planet_data, varga_szorzo):
    varga_positions = {}
    for planet, data in planet_data.items():
        longitude = data["longitude"] % 360.0
        varga_longitude = (longitude * varga_szorzo) % 360.0
        varga_positions[planet] = {"longitude": varga_longitude}
    return varga_positions
def calculate_all_varga_positions(planet_data: dict, varga_factors: dict) -> dict:
    """
    Feldolgozza az összes részhoroszkópot a varga_factor szótár alapján.
    Visszaad egy szótárat: { "D1": { "Moon": {...}, ... }, "D9": {...}, ... }
    """
    all_varga_positions = {}

    for varga_name, szorzo in varga_factors.items():
        varga_positions = {}
        for planet, data in planet_data.items():
            longitude = data.get("longitude", 0.0) % 360.0
            varga_longitude = (longitude * szorzo) % 360.0
            varga_positions[planet] = {"longitude": varga_longitude}
        all_varga_positions[varga_name] = varga_positions

    return all_varga_positions

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# 🪐 Bolygópozíció lekérdezése
def get_planet_position(jd: float, planet_id: int, flags: int = swe.FLG_SWIEPH) -> dict:
    try:
        result = swe.calc_ut(jd, planet_id, flags)
        lon = sanitize_number(result[0][0])
        lat = sanitize_number(result[0][1])
        dist = sanitize_number(result[0][2])
        return {"longitude": lon, "latitude": lat, "distance": dist}
    except Exception as e:
        print(f"Hiba történt a bolygópozíció lekérésekor: {e}")
        return {"longitude": None, "latitude": None, "distance": None}

# 🧠 Házbesorolás egyenlő házak esetén
def get_house_index(asc_degree, planet_degree):
    relative = (planet_degree - asc_degree) % 360
    return int(relative // 30) + 1

# 🌅 Aszcendens kiszámítása Swisseph-pel
def calculate_ascendant(jd_ut, latitude, longitude):
    try:
        cusps, ascmc = swe.houses(jd_ut, latitude, longitude)
        asc = ascmc[0]   # 0 index = Ascendens fokban
        return asc
    except Exception as e:
        print("Aszcendens számítási hiba:", e)
        return 0.0

# 🪐 Bolygóadatok + Rahu–Ketu + Aszcendens Swisseph alapján
def get_planet_data(jd=None, latitude=47.0, longitude=17.0):
    if jd is None:
        # ⏳ Pendulum használata
        now = pendulum.now("Europe/Budapest")
        jd = swe.julday(
            now.year,
            now.month,
            now.day,
            now.hour + now.minute / 60.0 + now.second / 3600.0,
        )

    # Aszcendens
    asc_degree = calculate_ascendant(jd, latitude, longitude)
    positions = {}

    planet_ids = {
        swe.SUN: "Sun",
        swe.MOON: "Moon",
        swe.MERCURY: "Mercury",
        swe.VENUS: "Venus",
        swe.MARS: "Mars",
        swe.JUPITER: "Jupiter",
        swe.SATURN: "Saturn",
        swe.URANUS: "Uranus",
        swe.NEPTUNE: "Neptune",
        swe.PLUTO: "Pluto",
    }

    # 🌌 Bolygók pozíciói
    for pid, name in planet_ids.items():
        result, _ = swe.calc_ut(jd, pid)
        lon = result[0]
        speed = result[3]
        sign = SIGNS[int(lon // 30)]
        retrograde = speed < 0
        house = get_house_index(asc_degree, lon)
        positions[name] = {
            "longitude": lon,
            "sign": sign,
            "retrograde": retrograde,
            "speed": speed,
            "house": house,
        }

    # 🌗 Rahu (Északi Holdcsomópont) és Ketu (Déli Holdcsomópont)
    rahu_result, _ = swe.calc_ut(jd, swe.TRUE_NODE)  # vagy swe.MEAN_NODE
    rahu_lon = rahu_result[0]
    ketu_lon = (rahu_lon + 180.0) % 360.0

    rahu_house = get_house_index(asc_degree, rahu_lon)
    ketu_house = get_house_index(asc_degree, ketu_lon)

    positions["Rahu"] = {
        "longitude": rahu_lon,
        "sign": SIGNS[int(rahu_lon // 30)],
        "retrograde": True,
        "speed": rahu_result[3],
        "house": rahu_house,
    }
    positions["Ketu"] = {
        "longitude": ketu_lon,
        "sign": SIGNS[int(ketu_lon // 30)],
        "retrograde": True,
        "speed": -rahu_result[3],
        "house": ketu_house,
    }

    # 🧭 Aszcendens
    positions["ASC"] = {
        "longitude": asc_degree,
        "sign": SIGNS[int(asc_degree // 30)],
        "house": 1,
    }

    return positions
# 🔄 Egyszerű alias

def last_planet_positions(date: pendulum.DateTime, latitude=47.0, longitude=17.0):
    jd = swe.julday(
        date.year,
        date.month,
        date.day,
        date.hour + date.minute / 60.0 + date.second / 3600.0,
    )
    return get_planet_data(jd, latitude, longitude)

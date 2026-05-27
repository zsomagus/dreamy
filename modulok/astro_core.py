# modulok/astro_core.py
import os
from datetime import datetime
import jyotishganit
from jyotishganit import calculate_birth_chart
import pendulum

from modulok.config import YANTRA_PATH
from modulok.tables import varga_factors

def calculate_nakshatra(longitude, ayanamsa, nakshatras):
    sidereal_longitude = (longitude - ayanamsa) % 360
    nakshatra_index = int(sidereal_longitude // 13.3333) % 27
    nakshatra = nakshatras[nakshatra_index]
    pada = int((sidereal_longitude % 13.3333) // 3.3333) + 1
    return nakshatra, pada

def find_yantra_by_tithi(tithi, yantra_folder=YANTRA_PATH):
    if not os.path.exists(yantra_folder):
        return None
        
    # Kinyerjük a tithi sorszámát (ha pl. szövegként vagy objektumként jönne)
    tithi_szam = str(tithi)
    if hasattr(tithi, "number"):
        tithi_szam = str(tithi.number)
    elif isinstance(tithi, str):
        # Ha szövegesen tartalmazza a Védikus elnevezést
        tithi_nevek = ["pratipat", "dwitiya", "tritiya", "chaturthi", "panchami", "shashti", 
                       "saptami", "ashtami", "navami", "dashami", "ekadashi", "dwadashi", 
                       "trayodashi", "chaturdashi", "purnima", "amavasya"]
        for i, nev in enumerate(tithi_nevek):
            if nev in tithi.lower():
                # Shukla (1-15), Krishna (16-30)
                eltolas = 15 if "krishna" in tithi.lower() else 0
                tithi_szam = str(i + 1 + eltolas)
                break

    # Csak a tiszta számjegyeket tartjuk meg (pl. "12")
    tithi_szam = "".join([c for c in tithi_szam if c.isdigit()])
    if not tithi_szam:
        return None

    for fname in os.listdir(yantra_folder):
        if fname.lower().endswith(".jpg"):
            # Ellenőrizzük, hogy a fájlnév eleje egyezik-e a tithi számával (pl. "12.jpg" vagy "12_yantra.jpg")
            alap_nev = fname.split(".")[0].split("_")[0]
            if alap_nev == tithi_szam:
                return os.path.join(yantra_folder, fname)
    return None
def extract_varga_code(label: str) -> str:
    return label.split()[0]

def get_varga_factor(label: str) -> float:
    return varga_factors.get(label, 1.0)

def get_varga_chart_data(year: int, month: int, day: int, hour: int, minute: int,
                         lat: float, lon: float, timezone_offset: float,
                         varga_label: str = "D1 (Rashi)"):
    birth_date = datetime(year, month, day, hour, minute, 0)
    
    chart = calculate_birth_chart(
        birth_date=birth_date,
        latitude=lat,
        longitude=lon,
        timezone_offset=timezone_offset,
    )

    varga_code = extract_varga_code(varga_label)
    
    if varga_code == "D1":
        rasi_chart = chart.d1_chart
    else:
        rasi_chart = chart.divisional_charts.get(varga_code)
        if rasi_chart is None:
            raise ValueError(f"Nincs ilyen varga: {varga_code}")
    
    planet_data = {}
    
    # 🎯 OKOSÍTÁS: Biztonságosan kinyerjük az ayanamsa értékét számmá alakítva (float)
    raw_ayanamsa = getattr(chart, "ayanamsa", 24.24)
    try:
        ayanamsa_val = float(raw_ayanamsa)
    except (TypeError, ValueError):
        if hasattr(raw_ayanamsa, "value"):
            ayanamsa_val = float(raw_ayanamsa.value)
        else:
            ayanamsa_val = 24.24

    # Védikus jegyek sorrendje (1-től 12-ig)
    jegy_sorrend = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    for p in rasi_chart.planets:
        pname = p.celestial_body
        
        # 🎯 JAVÍTÁS: A szöveges 'sign' mezőből keressük ki a jegy sorszámát (1-12)
        angol_jegy = getattr(p, "sign", "Aries")
        if angol_jegy in jegy_sorrend:
            vedic_sign_1_12 = jegy_sorrend.index(angol_jegy) + 1
        else:
            vedic_sign_1_12 = 1  # Fallback a biztonság kedvéért
            
        sign_index = vedic_sign_1_12 - 1
        rasi_deg = float(p.sign_degrees)
        
        planet_data[pname] = {
            "longitude": float((sign_index * 30) + rasi_deg), # Tiszta sziderikus védikus fok
            "vedic_sign": vedic_sign_1_12,                    # Garantáltan jó jegyszám (1-12)
            "rasi_deg": rasi_deg,                             # Fok a jegyen belül (0-30)
            "sign": angol_jegy,
            "nakshatra": p.nakshatra,
            "house": p.house,
            "rashi_lord": getattr(p, "rashi_lord", None) or "Unknown",
            "nakshatra_lord": getattr(p, "nakshatra_lord", None) or "Unknown"
        }
    # 🎯 JAVÍTÁS: Kinyerjük az Aszcendens (Ascendant) sziderikus jegyét és adatait
    if hasattr(rasi_chart, "ascendant") and rasi_chart.ascendant:
        asc_obj = rasi_chart.ascendant
        angol_jegy = getattr(asc_obj, "sign", "Aries")
        
        if angol_jegy in jegy_sorrend:
            asc_vedic_sign = jegy_sorrend.index(angol_jegy) + 1
        else:
            asc_vedic_sign = 1
            
        planet_data["ASC"] = {
            "vedic_sign": asc_vedic_sign,
            "rasi_deg": float(getattr(asc_obj, "sign_degrees", 0.0)),
            "sign": angol_jegy
        }
    return {
        "varga_label": varga_label,
        "varga_code": varga_code,
        "factor": get_varga_factor(varga_label),
        "planet_data": planet_data,
        "chart_obj": chart,
        "rasi_chart": rasi_chart,
        "tithi": chart.panchanga.tithi,
        "nakshatra": chart.panchanga.nakshatra,
    }

def compute_full_chart_for_gui(bd: dict, varga_label: str):
    year = int(bd["date"].split("-")[0])
    month = int(bd["date"].split("-")[1])
    day = int(bd["date"].split("-")[2])
    hour = int(bd["time"].split(":")[0])
    minute = int(bd["time"].split(":")[1])
    lat = float(bd["lat"] or 47.0)
    lon = float(bd["lon"] or 19.0)

    tz = pendulum.timezone(bd["timezone"])
    dt = tz.datetime(year, month, day, hour, minute)
    timezone_offset = dt.utcoffset().total_seconds() / 3600

    res = get_varga_chart_data(
        year=year, month=month, day=day, hour=hour, minute=minute,
        lat=lat, lon=lon, timezone_offset=timezone_offset,
        varga_label=varga_label
    )

    # CRITICAL: Szigorúan helyi import, hogy elkerüljük a körkörös hivatkozást!

    # 1. Alap horoszkóp rajzolása
    svg_rasi, png_rasi = draw.rajzol_del_indiai_horoszkop_svg(
        varga_pos=res, bd=bd, planet_data=res["planet_data"], 
        varga_name=res["varga_label"], tithi=res["tithi"], horoszkop_nev=res["varga_code"]
    )

    # 2. Urak (Lords) térképeinek legenerálása a draw_lord modul segítségével
    png_rashi_lord = draw_lord.generate_rashi_lord_chart(res, bd)
    png_nakshatra_lord = draw_lord.generate_nakshatra_lord_chart(res, bd)

    summary_text = f"Tithi: {res['tithi']}\nNakshatra: {res['nakshatra']}\nVarga: {res['varga_code']}"

    return {
        "chart": res["chart_obj"],
        "varga_chart": res["rasi_chart"],
        "panchanga": res["chart_obj"].panchanga,
        "summary": summary_text,
        "svg_path": svg_rasi,
        "png_path": png_rasi,
        "png_rashi_lord": png_rashi_lord,
        "png_nakshatra_lord": png_nakshatra_lord,
        "planet_data": res["planet_data"]
    }
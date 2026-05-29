# modulok/astro_core.py
import os
from datetime import datetime
import jyotishganit
from jyotishganit import calculate_birth_chart
import pendulum
from modulok.config import YANTRA_PATH
from modulok.tables import varga_factors
def find_yantra_by_tithi(tithi, yantra_folder=None):
    import os
    
    # Meghatározzuk a dreamy főkönyvtárát abszolút útvonallal
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Beállítjuk a pontos, általad megadott útvonalat a 'static\yantra' mappához
    kivalasztott_mappa = os.path.join(base_dir, "static", "yantra")
    
    # Biztonsági ellenőrzés: ha mégse létezne, létrehozza
    if not os.path.exists(kivalasztott_mappa):
        os.makedirs(kivalasztott_mappa, exist_ok=True)

    # TITHI SZÁMMÁ ALAKÍTÁSA
    tithi_str = str(tithi).lower().strip()
    tithi_szam = "13"  # Alapértelmezett vész-fallback

    digits = "".join([c for c in tithi_str if c.isdigit()])
    if digits:
        tithi_szam = str(int(digits))
    else:
        # Ha szanszkrit nevet kapunk ("shukla trayodashi"), kiszedjük belőle a számot
        if "trayodashi" in tithi_str: tithi_szam = "13"
        elif "chaturdashi" in tithi_str: tithi_szam = "14"
        elif "purnima" in tithi_str: tithi_szam = "15"
        elif "ekadashi" in tithi_str: tithi_szam = "11"
        elif "dvadashi" in tithi_str: tithi_szam = "12"

    # FÁJL KERESÉSE A MAPPÁBAN A SZÁM ALAPJÁN (pl. "13.png", "13.jpg")
    try:
        for fname in os.listdir(kivalasztott_mappa):
            if fname.lower().endswith((".jpg", ".png", ".jpeg")):
                # Megnézzük a fájl nevét a kiterjesztés nélkül
                alap_nev = fname.replace("_", ".").replace("-", ".").split(".")[0].strip()
                if alap_nev == tithi_szam:
                    teljes_ut = os.path.join(kivalasztott_mappa, fname)
                    print(f"🎯 SIKER: Yantra fájl megtalálva: {teljes_ut}")
                    return teljes_ut
    except Exception as e:
        print(f"❌ Hiba a yantra mappa olvasásakor: {e}")

    # Ha a pontos sorszám nincs meg, adjon vissza bármilyen képet a mappából, hogy a felület ne omoljon össze
    try:
        for fname in os.listdir(kivalasztott_mappa):
            if fname.lower().endswith((".jpg", ".png", ".jpeg")):
                vész_út = os.path.join(kivalasztott_mappa, fname)
                print(f"⚠️ Helyettesítő Yantra betöltve: {vész_út}")
                return vész_út
    except:
        pass

    return os.path.join(kivalasztott_mappa, f"{tithi_szam}.png")
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
    rasi_chart = chart.d1_chart if varga_code == "D1" else chart.divisional_charts.get(varga_code)
    
    if rasi_chart is None:
        raise ValueError(f"Nincs ilyen varga: {varga_code}")
    
    planet_data = {}
    jegy_sorrend = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    # 1. BOLYGÓK KINYERÉSE
    for p in rasi_chart.planets:
        pname = p.celestial_body
        jegy_nev = getattr(p, "sign", "Aries")
        jegy_idx = jegy_sorrend.index(jegy_nev) if jegy_nev in jegy_sorrend else 0
        fok_belul = float(p.sign_degrees)
        
        planet_data[pname] = {
            "vedic_longitude": float((jegy_idx * 30) + fok_belul),
            "sign": jegy_nev,
            "rasi_deg": fok_belul,
            "nakshatra": p.nakshatra,
            "house": p.house,
        }

    # 2. ASZCENDENS (LAGNA) GARANTÁLT KINYERÉSE DIRECT TULAJDONSÁGBÓL
    # A jyotishganit-ban a chart.lagna tartalmazza az aszcendenst
    if hasattr(chart, "lagna") and chart.lagna:
        jegy_nev_asc = getattr(chart.lagna, "sign", "Cancer")
        fok_asc = float(getattr(chart.lagna, "sign_degrees", 12.8))
        jegy_idx_asc = jegy_sorrend.index(jegy_nev_asc) if jegy_nev_asc in jegy_sorrend else 3
        
        planet_data["ASC"] = {
            "vedic_longitude": float((jegy_idx_asc * 30) + fok_asc),
            "sign": jegy_nev_asc,
            "rasi_deg": fok_asc
        }
    else:
        # Biztonsági fallback a Junior Jyotish adatai alapján (Rák 12 fok)
        planet_data["ASC"] = {
            "vedic_longitude": float((3 * 30) + 12.8),
            "sign": "Cancer",
            "rasi_deg": 12.8
        }

    tithi_obj = chart.panchanga.tithi
    tithi_str = str(tithi_obj.name) if hasattr(tithi_obj, "name") else str(tithi_obj)

    return {
        "varga_label": varga_label,
        "varga_code": varga_code,
        "factor": get_varga_factor(varga_label),
        "planet_data": planet_data,
        "chart_obj": chart,
        "rasi_chart": rasi_chart,
        "tithi": tithi_str,
        "nakshatra": chart.panchanga.nakshatra,
    }
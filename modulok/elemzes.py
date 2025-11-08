import swisseph as swe
import pyttsx3  # noqa: F401
import pendulum  # ✅
from modulok import tables, astro_core
from modulok.astro_core import calculate_nakshatra, get_house_index, calculate_ascendant
from modulok.tables import purushartha_map, bolygo_nakshatra_map, haz_aspektusok, haz_bolygo_aspektusok, nakshatras
from modulok.draw import rajzol_del_indiai_horoszkop
from modulok.config import BASE_DIR
from collections import Counter
import pandas as pd
from modulok.dasa_tools import generate_dasa_summary
from markdown import markdown
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import re


# 📥 Adatbázis betöltése
excel_path = BASE_DIR / "static" / "asztrológiai_adatbázis.xlsx"
jegyek_df = pd.read_excel(excel_path, sheet_name="Jegyek")
hazak_df = pd.read_excel(excel_path, sheet_name="Házak")
bolygok_df = pd.read_excel(excel_path, sheet_name="Bolygók")
nakshatra_df = pd.read_excel(excel_path, sheet_name="Nakshatra _ Pada")


def load_excel(filename, sheet):
    path = BASE_DIR / "static" / filename
    return pd.read_excel(path, sheet_name=sheet)


# 🔍 Értelmező függvények
def get_jegy_info(jegy):
    match = jegyek_df[jegyek_df["Jegy"] == jegy]
    return match.iloc[0]["Tulajdonságok"] if not match.empty else "Ismeretlen jegy."


def get_haz_info(haz_szam):
    match = hazak_df[hazak_df["Ház száma"] == haz_szam]
    if not match.empty:
        return (
            f"{match.iloc[0]['Tulajdonságok']} "
            f"– Purushartha: {purushartha_map(haz_szam)}"
        )
    return "Ismeretlen ház."


def get_bolygo_info(bolygo):
    match = bolygok_df[bolygok_df["Bolygó"] == bolygo]
    return match.iloc[0]["Tulajdonságok"] if not match.empty else "Ismeretlen bolygó."


def get_purushartha(pada):
    return ["Dharma", "Artha", "Kama", "Moksha"][pada - 1]


def get_purushartha_info(haz_szam, pada_szam):
    return tables.purushartha_map.get(haz_szam, {}).get(
        pada_szam, ("Ismeretlen", "Nincs leírás")
    )


def get_haz_aspektus(haz_szam):
    return tables.haz_aspektusok.get(haz_szam, ("Ismeretlen", "Nincs leírás"))


def get_haz_bolygo_aspektus(haz_szam):
    bolygo, leiras = haz_bolygo_aspektusok.get(
        haz_szam, (None, "Ismeretlen ház vagy nincs leírás.")
    )
    if bolygo:
        return f"{bolygo} – {leiras}"
    return leiras


def get_nakshatra_info(nakshatra, pada):
    match = nakshatra_df[nakshatra_df["Nakshatra"] == nakshatra]
    if not match.empty:
        col = f"{pada}. Páda ({get_purushartha(pada)})"
        return (
            match.iloc[0][col] if col in match.columns else "Hiányzó pada értelmezés."
        )
    return "Ismeretlen nakshatra vagy pada."


# 📝 Szöveg generálása
def generate_markdown_summary(positions, aspektusok_lista, birth_data=None):
    ayanamsa = birth_data.get("ayanamsa") if birth_data else None
    if not ayanamsa:
        now = pendulum.now("Europe/Budapest")
        jd = astro_core.swe.julday(now.year, now.month, now.day, 12.0)
        ayanamsa = astro_core.get_ayanamsa(jd)

    md = "# 🌠 Asztrológiai Elemzés\n\n"

    for bolygo, adat in positions.items():
        if bolygo == "ASC":
            continue

        jegy = adat["sign"]
        haz = adat["house"]
        nakshatra = adat.get("nakshatra")
        pada = adat.get("pada")
        if not nakshatra or not pada:
            nakshatra, pada = astro_core.calculate_nakshatra(
                adat["longitude"], ayanamsa, nakshatras
            )

        md += f"## 🔹 {bolygo}\n"
        md += f"- **Jegy**: {jegy}\n"
        md += f"- **Ház**: {haz}\n"
        md += f"- **Nakshatra**: {nakshatra}\n"
        md += f"- **Pada**: {pada}\n"
        md += f"- **Tulajdonságok**: {get_bolygo_info(bolygo)}\n"
        md += f"- **Jegy jellemzői**: {get_jegy_info(jegy)}\n"
        md += f"- **Ház jellemzői**: {get_haz_info(haz)}\n"
        md += f"- **Nakshatra értelmezés**: {get_nakshatra_info(nakshatra, pada)}\n\n"

    md += "## 🌌 Aspektusok\n"
    for asp in aspektusok_lista:
        haz_from = positions[asp["from"]]["house"]
        bolygo_from = asp["from"]

        aspektus, leiras = get_haz_aspektus(haz_from)
        md += f"- **Ház aspektus**: {aspektus} – {leiras}\n"

        bolygo_aspektus = get_haz_bolygo_aspektus(haz_from, bolygo_from)
        md += f"- **Ház bolygó-aspektus**: {bolygo_aspektus}\n"

        pada = positions[bolygo_from].get("pada", 1)
        purushartha, leiras = get_purushartha_info(haz_from, pada)
        md += f"- **Purushartha**: {purushartha} – {leiras}\n\n"

    # 🕰️ Dasa ciklusok hozzáadása
    if birth_data:
        dasa_text = generate_dasa_summary(birth_data)
        md += "\n## 🕰️ Dasa ciklusok\n"
        md += dasa_text + "\n"

    for bolygo, adat in positions.items():
        jegy = adat["sign"]
        haz = adat["house"]
        summary_text = md  # vagy bolygóspecifikus részlet
        vizualis_prompts = generate_visuals_from_summary(summary_text, bolygo, jegy, str(haz))
        md += f"\n## 🎨 {bolygo} vizuális archetípusai\n"
        for i, prompt in enumerate(vizualis_prompts, 1):
            md += f"- Kép {i}: *{prompt}*\n"

    return md


def summarize_purusharthas(purushartha_list):
    count = Counter(purushartha_list)
    summary = "\n## 🧭 Purushartha Összegzés\n"
    for p, c in count.items():
        summary += f"- **{p}**: {c} bolygó kapcsolódik ehhez az életcélhoz\n"
    return summary


# 💾 Mentés Markdown fájlba
def save_markdown(text, filename="elemzes.md"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)




def save_analysis_pdf(md_text, person_name):
    # Fájlnév a személy nevéből
    safe_name = re.sub(r"[^\w\-]", "_", person_name.strip())
    filename = f"{safe_name}_elemzes.pdf"

    # PDF létrehozása
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 2 * cm
    y = height - margin

    # Szöveg feldarabolása sorokra
    lines = md_text.split("\n")
    c.setFont("Helvetica", 11)

    for line in lines:
        if y < margin:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - margin
        c.drawString(margin, y, line)
        y -= 14  # sor magasság

    c.save()
    return filename

# 🔊 Hang mentése WAV fájlba
def save_audio(text, filename="elemzes.wav"):
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)
    engine.save_to_file(text, filename)
    engine.runAndWait()


# 🧩 GUI gomb callback

# modulok/elemzes.py


def teszt():
    print("Elemzés modul működik!")



def save_analysis_pdf(md_text, person_name):
    # Fájlnév a személy nevéből
    safe_name = re.sub(r"[^\w\-]", "_", person_name.strip())
    filename = f"{safe_name}_elemzes.pdf"

    # PDF létrehozása
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    margin = 2 * cm
    y = height - margin

    # Szöveg feldarabolása sorokra
    lines = md_text.split("\n")
    c.setFont("Helvetica", 11)

    for line in lines:
        if y < margin:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - margin
        c.drawString(margin, y, line)
        y -= 14  # sor magasság

    c.save()
    return filename


def generate_full_analysis(
    date_str,
    time_str,
    timezone_str,
    latitude_str,
    longitude_str,
    vezeteknev,
    keresztnev,
    varga_nev="D1",
    is_prashna=False
):
    # 🧠 Adatcsomag összeállítása
    chart_data = build_chart_data(
        date_str,
        time_str,
        timezone_str,
        latitude_str,
        longitude_str,
        vezeteknev,
        keresztnev,
        varga_nev,
        is_prashna,
    )

    # 🎨 Horoszkóp rajzolása
    draw_chart(chart_data)

    # 📄 Markdown elemzés generálása
    md = generate_markdown_summary(
        chart_data["planet_data"],
        chart_data.get("aspektusok", []),
        chart_data,
    )

    # 🧭 Purushartha összegzés hozzáfűzése
    if "purushartha_list" in chart_data:
        from modulok.tables import purushartha_map
        md += summarize_purusharthas(chart_data["purushartha_list"])

    # 💾 PDF mentés
    filename = save_analysis_pdf(md, keresztnev)
    print(f"PDF mentve: {filename}")

    return chart_data, filename
def generate_full_analysis_with_visual(chart_data):
    draw_chart(chart_data)  # 🎨 kép generálás

    # 🖼️ Markdown fejléc kép + metaadat
    image_name = f"{chart_data['vezeteknev'].lower()}_{chart_data['keresztnev'].lower()}_horoszkop_{chart_data['horoszkop_nev']}.png"
    md = f"![Horoszkóp](static/{image_name})\n\n"
    md += f"**Név**: {chart_data['keresztnev']} {chart_data['vezeteknev']}\n"
    md += f"**Dátum**: {chart_data['date_str']}\n"
    md += f"**Idő**: {chart_data['time_str']}\n"
    md += f"**Tithi**: {chart_data['tithi']}\n"
    md += f"**Horoszkóp típusa**: {chart_data['horoszkop_nev']}\n\n"

    # 🧠 Elemzés
    md += generate_markdown_summary(
        chart_data["planet_data"],
        chart_data.get("aspektusok", []),
        chart_data,
    )

    # 🧭 Purushartha összegzés
    if "purushartha_list" in chart_data:
        md += summarize_purusharthas(chart_data["purushartha_list"])

    # 💾 PDF mentés
    filename = save_analysis_pdf(md, chart_data["keresztnev"])
    print(f"PDF mentve: {filename}")
    return filename
def enrich_planet_data(chart_data):
    ayanamsa = chart_data.get("ayanamsa")
    if ayanamsa is None:
        from modulok.astro_core import get_ayanamsa
        jd = chart_data.get("jd_ut")
        if jd is None:
            raise ValueError("Hiányzik a jd_ut vagy ayanamsa a chart_data-ból.")
        ayanamsa = get_ayanamsa(jd)
        chart_data["ayanamsa"] = ayanamsa

    asc_deg = chart_data["planet_data"]["ASC"]["longitude"]

    for planet, data in chart_data["planet_data"].items():
        lon = data["longitude"]

        # 🌌 Nakshatra + Pada
        nakshatra, pada = calculate_nakshatra(lon, ayanamsa, nakshatras)
        data["nakshatra"] = nakshatra
        data["pada"] = pada

        # 🧭 Ház
        data["house"] = get_house_index(asc_deg, lon)

        # 👑 Nakshatra ura
        ura = ""
        for bolygo, lista in bolygo_nakshatra_map.items():
            if nakshatra in lista:
                ura = bolygo
                break
        data["nakshatra_ura"] = ura
def draw_chart(chart_data):
    planet_data = chart_data["planet_data"]
    tithi = chart_data["tithi"]

    # 🎨 Kép generálás
    rajzol_del_indiai_horoszkop(
        planet_data,
        tithi,
        horoszkop_nev=chart_data.get("horoszkop_nev", "D1"),
        date_str=chart_data.get("date_str"),
        time_str=chart_data.get("time_str"),
        vezeteknev=chart_data.get("vezeteknev"),
        keresztnev=chart_data.get("keresztnev"),
        is_prashna=chart_data.get("is_prashna", False),
    )


    # 📄 PDF elemzés
    md = generate_markdown_summary(
        chart_data["planet_data"],
        chart_data.get("aspektusok", []),
        chart_data,
    )
    filename = save_analysis_pdf(md, chart_data["keresztnev"])
    print(f"PDF mentve: {filename}")

def build_chart_data(
    date_str,
    time_str,
    timezone_str,
    latitude_str,
    longitude_str,
    vezeteknev,
    keresztnev,
    varga_nev,
    is_prashna=False
):
    # 🕰️ Dátum és idő konvertálása
    local_dt = pendulum.parse(f"{date_str}T{time_str}", tz=timezone_str)
    utc_dt = local_dt.in_timezone("UTC")

    # 📅 Julian Day
    jd_ut = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600,
    )

    latitude = float(latitude_str)
    longitude = float(longitude_str)

    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    asc_deg = calculate_ascendant(jd_ut, latitude, longitude)
    asc_sidereal = (asc_deg - ayanamsa) % 360

    # 🌌 Bolygópozíciók
    planet_data = {}
    for name, pid in tables.planet_ids.items():
        pos, _ = swe.calc_ut(jd_ut, pid)
        sidereal_pos = (pos[0] - ayanamsa) % 360
        planet_data[name] = {"longitude": sidereal_pos}
    planet_data["ASC"] = {"longitude": asc_sidereal}

    # 🌙 Tithi
    tithi = (
        int(
            ((planet_data["Moon"]["longitude"] - planet_data["Sun"]["longitude"]) % 360)
            / 12
        )
        + 1
    )

    # 🧭 Purushartha lista (opcionális)
    purushartha_list = []
    for name, data in planet_data.items():
        nakshatra, pada = astro_core.calculate_nakshatra(data["longitude"], ayanamsa, tables.nakshatras)
        purushartha = ["Dharma", "Artha", "Kama", "Moksha"][pada - 1]
        purushartha_list.append(purushartha)

    return {
        "planet_data": planet_data,
        "tithi": tithi,
        "horoszkop_nev": varga_nev,
        "date_str": date_str,
        "time_str": time_str,
        "timezone_str": timezone_str,
        "latitude": latitude,
        "longitude": longitude,
        "vezeteknev": vezeteknev,
        "keresztnev": keresztnev,
        "is_prashna": is_prashna,
        "varga_nev": varga_nev,
        "purushartha_list": purushartha_list,
    }

    return build_chart_data

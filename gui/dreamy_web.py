import os
import sys
import requests
# Megkeressük a gui mappa szülőmappáját (a projekt gyökerét)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
import pendulum
import streamlit as st
import pandas as pd
import gspread

from modulok import astro_core
from modulok import draw
from modulok.load_alomszotar import load_alomszotar
from modulok.music_prompt import build_music_prompt
from modulok.score_renderer import export_score_to_pdf_and_png

# =========================================================
# SESSION STATE INICIALIZÁLÁS (ÖSSZEOMLÁSVÉDELEM)
# =========================================================
if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""

if "music_prompt" not in st.session_state:
    st.session_state.music_prompt = ""

if "chart_path" not in st.session_state:
    st.session_state.chart_path = None

if "yantra_path" not in st.session_state:
    st.session_state.yantra_path = None

if "dream_log" not in st.session_state:
    # Az első indításkor automatikusan beolvassuk az eddigi álmokat a táblázatból
    # Így a feleséged azonnal látni fogja a régi naplóbejegyzéseit!
    try:
        # Mivel a függvényt később definiálod a kódban, meghívhatjuk közvetlenül, 
        # vagy csak üres listaként indítjuk, és az app alján töltjük be. 
        # Legyen biztonsági okokból elsőre egy üres lista:
        st.session_state.dream_log = []
    except:
        st.session_state.dream_log = []
# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Dreamy Widget",
    page_icon="🌙",
    layout="wide"
)

# PWA Regisztráció
pwa_html = """
<link rel="manifest" href="static/manifest.json">
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('static/service_worker.js')
        .then(function(reg) { console.log('Service Worker sikeresen regisztrálva!', reg); })
        .catch(function(err) { console.error('Service Worker regisztrációs hiba:', err); });
    });
  }
</script>
"""
st.components.v1.html(pwa_html, height=0, width=0)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
.main {
    background: linear-gradient(180deg,#0f0f1b,#19192e);
    color: white;
}
.stTextArea textarea {
    background-color: #141427 !important;
    color: white !important;
    border-radius: 12px;
}
.stTextInput input {
    background-color: #141427 !important;
    color: white !important;
}
.stSelectbox div[data-baseweb="select"] {
    background-color: #141427 !important;
}
.stButton button {
    background: linear-gradient(90deg,#7b2ff7,#f107a3);
    color: white;
    border-radius: 12px;
    border: none;
    font-weight: bold;
    padding: 0.7rem 1rem;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE SHEETS FUNKCIÓK (TISZTA, JAVÍTOTT VERZIÓ)
# =========================================================
def load_dreams_from_sheets():
    """Beolvassa az online naplót és összefésüli a Google Táblázat oszlopneveit a kód változóival"""
    try:
        sheet_url = st.secrets["google_sheets"]["sheet_url"]
        base_url = sheet_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        
        df = pd.read_csv(csv_url)
        
        # Ha a táblázat üres, ne csináljon semmit
        if df.empty:
            return []
            
        # HAJSZÁLPONTOS OSZLOP-ÖSSZEFÉSÜLÉS:
        # Megnézzük, mi a Google Táblázat valódi oszlopneve, és lefordítjuk a kód nyelvére
        mapping = {}
        if "Időbélyeg" in df.columns: mapping["Időbélyeg"] = "Időbélyeg"
        if "Dátum" in df.columns: mapping["Dátum"] = "Dátum"
        if "Hangulat" in df.columns: mapping["Hangulat"] = "Hangulat"
        if "Kulcsszavak" in df.columns: mapping["Kulcsszavak"] = "Kulcsszavak"
        if "Szimbólum" in df.columns: mapping["Szimbólum"] = "Szimbólum"
        if "Leírás" in df.columns: mapping["Leírás"] = "Leírás"
        
        # Ha a kódod régebbi verziója kisbetűs angol kulcsokat várna a megjelenítésnél, 
        # akkor ezt a biztonsági másolatot használjuk, hogy mindkét irányba működjön:
        renamed_df = df.rename(columns={
            "Időbélyeg": "timestamp",
            "Dátum": "date",
            "Hangulat": "mood",
            "Kulcsszavak": "keywords",
            "Szimbólum": "symbols",
            "Leírás": "description"
        })
        
        # Biztosítjuk, hogy az eredeti magyar nevek is megmaradjanak kulcsként, ha a táblázat-megjelenítő azt keresné
        records = []
        for _, row in df.iterrows():
            record = {}
            for col in df.columns:
                # Ha a cella értéke üres vagy NaN, alakítsuk üres szöveggé a None helyett
                val = row[col]
                if pd.isna(val):
                    val = ""
                record[col] = val
                
                # Lefordítjuk kisbetűsre is a biztonság kedvéért
                if col == "Időbélyeg": record["timestamp"] = val
                if col == "Dátum": record["date"] = val
                if col == "Hangulat": record["mood"] = val
                if col == "Kulcsszavak": record["keywords"] = val
                if col == "Szimbólum": record["symbols"] = val
                if col == "Leírás": record["description"] = val
            records.append(record)
            
        return records
    except Exception as e:
        st.error(f"Nem sikerült beolvasni az online naplót: {e}")
        return []

def save_dream_to_sheets(date_str, mood, keywords, symbols, description):
    """Új sort küld a Google Táblázatba böngésző álcázással (Headers)"""
    try:
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfnbGuNsXCFQNofdmwze7N6iJPWTrla1elXmvjugI7ZCEUv4g/formResponse"
        
        # Tisztítjuk a szimbólumokat
        tisztitott_szimbolumok = ", ".join(symbols) if isinstance(symbols, list) else str(symbols)
        
        # Az adatok, amiket be kell préselni a Google oszlopaiba
# BIZTONSÁGOS DÁTUM KEZELÉS: Bármi is érkezik (szöveg vagy dátum objektum), 
        # tiszta stringgé alakítjuk, és YYYY-MM-DD formátumra hozzuk
        import datetime
        if isinstance(date_str, (datetime.date, datetime.datetime)):
            tiszta_datum = date_str.strftime("%Y-%m-%d")
        else:
            tiszta_datum = str(date_str).replace('.', '-').replace('/', '-').strip()

        # Egyszerűsített, tiszta adatcsomag - a Google Form alapértelmezett szöveges POST-jához
        form_data = {
            "entry.1780751080": tiszta_datum,                      # Dátum (Index 0)
            "entry.848467000": str(mood).strip(),                  # Hangulat (Index 1)
            "entry.45759550": str(keywords).strip(),               # Kulcsszavak (Index 2)
            "entry.45765567": str(tisztitott_szimbolumok).strip(), # Szimbólum (Index 3)
            "entry.45755088": str(description).strip()              # Leírás (Index 4)
        }

        # Küldés hagyományos form-adatként, böngészőnek álcázva
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"
        }

        try:
            response = requests.post(form_url, data=form_data, headers=headers)
            if response.status_code == 200:
                st.success("Az álom sikeresen elmentve az online naplóba!")
            else:
                st.error(f"A Google szervere hibát jelzett: {response.status_code}")
        except Exception as e:
            st.error(f"Hiba történt a küldés során: {e}")
        # BÖNGÉSZŐ ÁLCA: Ezzel elhitetjük a Google-lel, hogy egy rendes Chrome böngésző küldi az adatot
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Elküldjük a kérést az álcázással együtt
        response = requests.post(form_url, data=form_data, headers=headers)
        
        if response.status_code == 200:
            return True
        else:
            st.error(f"Szerver hiba a mentésnél: {response.status_code}")
            return False
            
    except Exception as e:
        st.error(f"Hiba a mentés során: {e}")
        return False
# =========================================================
# LOAD DREAM DICTIONARY
# =========================================================

@st.cache_data
def cached_szotar_betoltes(path):
    return load_alomszotar(path)

ALOMSZOTAR_PATH = os.path.join(BASE_DIR, "alomszotar.json")
try:
    SZOTAR = cached_szotar_betoltes(ALOMSZOTAR_PATH)
except:
    SZOTAR = {"alomszotar": []}

# =========================================================
# HELPERS
# =========================================================

def levag_ragokat(szo: str):
    ragok = ["ban", "ben", "val", "vel", "hoz", "hez", "höz", "nak", "nek", "ból", "ből", "ről", "tól", "től"]
    for rag in ragok:
        if szo.lower().endswith(rag) and len(szo) > len(rag) + 2:
            return szo[:-len(rag)]
    return szo

def analyze_dream(text, keywords):
    talalatok = []
    szimbolumok = []
    szavak = [s.strip().lower() for s in text.split() if len(s.strip()) > 2]
    szavak_tovei = [levag_ragokat(s) for s in szavak]
    egyedi_kulcsszavak = [k.strip().lower() for k in keywords.split(",") if k.strip()]
    minden = list(set(szavak_tovei + egyedi_kulcsszavak))

    for szo in minden:
        if len(szo) < 3:
            continue
        for item in SZOTAR.get("alomszotar", []):
            if not isinstance(item, dict):
                continue
            kulcsszo = item.get("kulcsszo", "").lower().strip()
            if szo == kulcsszo or kulcsszo in szo:
                jelentesek = item.get("jelentesek", [])
                for j in jelentesek:
                    sor = f"• {kulcsszo.capitalize()}: {j}"
                    if sor not in talalatok:
                        talalatok.append(sor)
                if kulcsszo not in szimbolumok:
                    szimbolumok.append(kulcsszo)
    return talalatok, szimbolumok

def generate_prashna_chart(lat, lon):
    now = pendulum.now("Europe/Budapest")
    res = astro_core.get_varga_chart_data(
        year=now.year, month=now.month, day=now.day, hour=now.hour, minute=now.minute,
        lat=lat, lon=lon, timezone_offset=now.utcoffset().total_seconds() / 3600,
        varga_label="D1 (Rashi)"
    )
    svg_res, png_res = draw.rajzol_del_indiai_horoszkop(
        planet_data=res["planet_data"], tithi=res["tithi"], horoszkop_nev=res["varga_code"]
    )
    raw_tithi = str(res.get("tithi", "13")).lower()
    
    # Kikeressük az összes számjegyet a szövegből (pl. "tithi 14" -> 14, vagy "sukla 3" -> 3)
    import re
    szamok = re.findall(r'\d+', raw_tithi)
    
    if szamok:
        tithi_szam = int(szamok[0])
    else:
        tithi_szam = 0  # Biztonsági tartalék, ha a szövegben egyáltalán nincs szám
        
    yantra = astro_core.find_yantra_by_tithi(tithi_szam)
    return png_res, yantra
# =========================================================
# HEADER
# =========================================================

st.title("🌙 Dreamy Widget")
st.caption("Automata Felhős Álomnapló • AI Prompt • Prashna • Yantra")

# =========================================================
# LAYOUT
# =========================================================

left_col, right_col = st.columns([1, 1])

# =========================================================
# LEFT COLUMN
# =========================================================

with left_col:
    st.subheader("📝 Új álom")
    dream_text = st.text_area("Mit álmodtál?", height=180)
    mood = st.selectbox("Hangulat", ["Nyugodt", "Zaklatott", "Misztikus", "Félelmetes", "Boldog", "Zavaros", "Relaxált/Meditatív"])
    keywords = st.text_input("Kulcsszavak (vesszővel)")

    st.subheader("📍 Prashna koordináták")
    lat = st.number_input("Szélesség", value=46.8572)
    lon = st.number_input("Hosszúság", value=18.1533)

    if st.button("✨ Mentés és értelmezés"):
        if dream_text.strip():
            talalatok, szimbolumok = analyze_dream(dream_text, keywords)
            if talalatok:
                st.session_state.analysis_text = "🔮 Értelmezések\n\n" + "\n".join(talalatok)
            else:
                st.session_state.analysis_text = "❌ Nincs találat az álomszótárban."

            prompt = build_music_prompt(dream_text, mood, keywords, szimbolumok)
            st.session_state.music_prompt = prompt
            now = pendulum.now("Europe/Budapest")
            date_str = now.format("YYYY-MM-DD HH:mm")

            # Mentés a Google Felhőbe
            with st.spinner("Álom mentése a felhőbe..."):
                if save_dream_to_sheets(date_str, mood, keywords, szimbolumok, dream_text):
                    st.success("🎯 Az álom sikeresen elmentve az online naplóba!")
                    # Frissítjük a helyi listát is, hogy azonnal látszódjon a táblázatban
                    st.session_state.dream_log = load_dreams_from_sheets()

            try:
                chart_path, yantra_path = generate_prashna_chart(lat, lon)
                st.session_state.chart_path = chart_path
                st.session_state.yantra_path = yantra_path
            except Exception as e:
                st.error(f"Horoszkóp hiba: {e}")

    st.subheader("🔮 Értelmezés")
    st.text_area("Értelmezés", value=st.session_state.analysis_text, height=200, label_visibility="collapsed")
    
    st.subheader("🎵 AI Prompt")
    st.code(st.session_state.music_prompt, language="markdown")

# =========================================================
# RIGHT COLUMN
# =========================================================

with right_col:
    tabs = st.tabs(["📊 Prashna", "🔮 Yantra", "📜 Online Napló"])

    # PRASHNA
    with tabs[0]:
        if st.session_state.chart_path and os.path.exists(st.session_state.chart_path):
            st.image(st.session_state.chart_path, width="stretch")
        else:
            st.info("Még nincs generált horoszkóp.")

    # YANTRA
    with tabs[1]:
        if st.session_state.yantra_path and os.path.exists(st.session_state.yantra_path):
            st.image(st.session_state.yantra_path, width=500)
        else:
            st.info("Még nincs yantra.")

    # ONLINE NAPLÓ MEGJELENÍTÉSE
    with tabs[2]:
        st.subheader("📜 Mentett álmok a Google Táblázatból")
        
        if st.session_state.dream_log:
            df = pd.DataFrame(st.session_state.dream_log)
            # Megfordítjuk a sorrendet, hogy a legfrissebb álom legyen legfelül
            df = df.iloc[::-1]
            st.dataframe(df, width="stretch")
        else:
            st.info("Az online napló még üres. Írd meg az első álmodat!")
       
        # Ha az app betöltődött és még üres a helyi memória logja, olvassa be a táblázatot
if not st.session_state.dream_log:
    st.session_state.dream_log = load_dreams_from_sheets()
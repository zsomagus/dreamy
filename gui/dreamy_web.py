import os
import sys
import requests
import json
import pendulum
import streamlit as st
import pandas as pd
import gspread
import re

# Megkeressük a gui mappa szülőmappáját (a projekt gyökerét)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

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
    """Beolvassa az online naplót és szigorúan csak a Google Táblázat valódi oszlopait mutatja meg"""
    try:
        sheet_url = st.secrets["google_sheets"]["sheet_url"]
        base_url = sheet_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
        
        df = pd.read_csv(csv_url)
        
        if df.empty:
            return []
            
        # CSAK a valódi magyar oszlopokat tartjuk meg, semmi duplázás vagy angolra fordítás!
        szurt_records = []
        for _, row in df.iterrows():
            timestamp = row.get("Időbélyeg", "")
         #   datum = row.get("Dátum", "")
            mood = row.get("Hangulat", "")
            keywords = row.get("Kulcsszavak", "")
            symbols = row.get("Szimbólum", "")
            description = row.get("Leírás", "")
            
            # NaN értékek (üres cellák) tisztítása szöveggé
            timestamp = "" if pd.isna(timestamp) else str(timestamp)
          #  datum = "" if pd.isna(datum) else str(datum)
            mood = "" if pd.isna(mood) else str(mood)
            keywords = "" if pd.isna(keywords) else str(keywords)
            symbols = "" if pd.isna(symbols) else str(symbols)
            description = "" if pd.isna(description) else str(description)
            
            szurt_records.append({
                "Időbélyeg": timestamp,
        #        "Dátum": datum,
                "Hangulat": mood,
                "Kulcsszavak": keywords,
                "Szimbólum": symbols,
                "Leírás": description
            })
            
        return szurt_records
    except Exception as e:
        st.error(f"Nem sikerült beolvasni az online naplót: {e}")
        return []

def save_dream_to_sheets(date_str, mood, keywords, symbols, description):
    """Új sort küld a Google Táblázatba a dátummező szándékos elhagyásával"""
    try:
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfnbGuNsXCFQNofdmwze7N6iJPWTrla1elXmvjugI7ZCEUv4g/formResponse"
        
        # Tisztítjuk a szimbólumokat
        tisztitott_szimbolumok = ", ".join(symbols) if isinstance(symbols, list) else str(symbols)
        
        # Teljesen kihagyjuk a dátumot, és a VALÓDI Google Form entry kódokat használjuk!
        form_data = {
            "entry.245253427": str(mood).strip(),                  # Hangulat
            "entry.60222006": str(keywords).strip(),               # Kulcsszavak
            "entry.718624254": str(tisztitott_szimbolumok).strip(), # Szimbólum
            "entry.1596218239": str(description).strip()            # Leírás
        }

        response = requests.post(form_url, data=form_data)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Hiba a Google szerverén: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Hiba történt a küldés során: {e}")
        return False

# =========================================================
# LOAD DREAM DICTIONARY (BEHÚZÁSOK JAVÍTVA!)
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
    
    szamok = re.findall(r'\d+', raw_tithi)
    if szamok:
        tithi_szam = int(szamok[0])
    else:
        tithi_szam = 0
        
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
                    # Frissítjük a helyi listát is az azonnali frissüléshez
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
            st.image(st.session_state.chart_path, use_container_width=True)
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
            df = df.iloc[::-1]  # Legfrissebb felülre
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Az online napló még üres. Írd meg az első álmodat!")
       
# Kezdeti beolvasás az alkalmazás indításakor
if not st.session_state.dream_log:
    st.session_state.dream_log = load_dreams_from_sheets()
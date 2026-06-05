import os
import sys

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
# GOOGLE SHEETS FUNKCIÓK
# =========================================================

def get_google_sheet():
    """Összekapcsolódik a Google Táblázattal a Streamlit Secrets segítségével"""
    try:
        # A Streamlit Cloud felületén megadott URL-t használjuk
        sheet_url = st.secrets["google_sheets"]["sheet_url"]
        # Anonim/Publikus szerkesztőként lépünk be, nem kell bonyolult json kulcsfájl
        gc = gspread.oauth_from_dict({}) if hasattr(gspread, 'oauth_from_dict') else gspread.public()
        # Megnyitjuk a táblázatot a link alapján
        sh = gc.open_by_url(sheet_url)
        return sh.sheet1
    except Exception as e:
        st.error(f"Nem sikerült kapcsolódni a Google Táblázathoz: {e}")
        return None

def load_dreams_from_sheets():
    """Beolvassa az összes eddigi álmot a Google Táblázatból"""
    sheet = get_google_sheet()
    if sheet:
        try:
            records = sheet.get_all_records()
            return records
        except:
            return []
    return []

def save_dream_to_sheets(date_str, mood, keywords, symbols, description):
    """Új sort ad hozzá a Google Táblázathoz"""
    sheet = get_google_sheet()
    if sheet:
        try:
            symbols_str = ", ".join(symbols) if isinstance(symbols, list) else str(symbols)
            sheet.append_row([date_str, mood, keywords, symbols_str, description])
            return True
        except Exception as e:
            st.error(f"Hiba a mentés során: {e}")
            return False
    return False

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================

if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""

if "music_prompt" not in st.session_state:
    st.session_state.music_prompt = ""

if "chart_path" not in st.session_state:
    st.session_state.chart_path = None

if "yantra_path" not in st.session_state:
    st.session_state.yantra_path = None

# Minden indításkor vagy frissítéskor frissítjük az álmok listáját a felhőből
st.session_state.dream_log = load_dreams_from_sheets()

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
# =========================================================
# STREAMLIT ÁLOMNAPLÓ WIDGET - OFFLINE EXCEL/CSV VERZIÓ
# =========================================================
import os
import sys
import json
import pendulum
import streamlit as st
import pandas as pd
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
# HELYI EXCEL/CSV STRUKTÚRA BEÁLLÍTÁSA (DOKUMENTUMOK MAPPA)
# =========================================================
# Dinamikusan megkeresi a te Windows felhasználói Dokumentumok mappádat
DOCUMENTS_DIR = os.path.join(os.path.expanduser("~"), "Documents")
LOCAL_DB_PATH = os.path.join(DOCUMENTS_DIR, "dream_log.csv")

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
st.html(pwa_html)

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
# HELYI FÁJL FUNKCIÓK (A GOOGLE HELYETT)
# =========================================================
def load_dreams_from_local():
    """Beolvassa a helyi Dokumentumok mappából az álomnaplót"""
    try:
        if not os.path.exists(LOCAL_DB_PATH):
            return []
        
        df = pd.read_csv(LOCAL_DB_PATH, encoding="utf-8")
        # NaN értékek és üres sorok kigyomlálása, hogy szép legyen a felület
        df = df.dropna(how="all")
        df = df.fillna("")
        
        return df.to_dict(orient="records")
    except Exception as e:
        st.error(f"Nem sikerült beolvasni a helyi naplót: {e}")
        return []

def save_dream_to_local(date_str, mood, keywords, symbols, description):
    """Elmenti az új álmot a gép Dokumentumok mappájában lévő táblázatba"""
    try:
        tisztitott_szimbolumok = ", ".join(symbols) if isinstance(symbols, list) else str(symbols)
        
        új_sor = {
            "Időbélyeg": date_str,
            "Hangulat": str(mood).strip(),
            "Kulcsszavak": str(keywords).strip(),
            "Szimbólum": str(tisztitott_szimbolumok).strip(),
            "Leírás": str(description).strip()
        }
        
        if os.path.exists(LOCAL_DB_PATH):
            df = pd.read_csv(LOCAL_DB_PATH, encoding="utf-8")
        else:
            df = pd.DataFrame(columns=["Időbélyeg", "Hangulat", "Kulcsszavak", "Szimbólum", "Leírás"])
            
        df = pd.concat([df, pd.DataFrame([új_sor])], ignore_index=True)
        df.to_csv(LOCAL_DB_PATH, index=False, encoding="utf-8")
        return True
    except Exception as e:
        st.error(f"Hiba történt a helyi mentés során: {e}")
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
st.caption(f"Helyi Biztonságos Álomnapló • AI Prompt • Prashna • Fájl: {LOCAL_DB_PATH}")

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

            # MENTÉS A GÉPRE (Excel kompatibilis formátumban)
            with st.spinner("Álom mentése a gép Dokumentumok mappájába..."):
                if save_dream_to_local(date_str, mood, keywords, szimbolumok, dream_text):
                    st.success("🎯 Az álom sikeresen elmentve a Dokumentumok közé!")
                    st.session_state.dream_log = load_dreams_from_local()

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
    tabs = st.tabs(["📊 Prashna", "🔮 Yantra", "📜 Helyi Napló"])

    # PRASHNA
    with tabs[0]:
        if st.session_state.chart_path and os.path.exists(st.session_state.chart_path):
            st.image(st.session_state.chart_path, width='stretch')
        else:
            st.info("Még nincs generált horoszkóp.")

    # YANTRA
    with tabs[1]:
        if st.session_state.yantra_path and os.path.exists(st.session_state.yantra_path):
            st.image(st.session_state.yantra_path, width=500)
        else:
            st.info("Még nincs yantra.")

    # HELYI NAPLÓ MEGJELENÍTÉSE
    with tabs[2]:
        st.subheader("📜 Dokumentumok mappába elmentett álmok")
        
        if st.session_state.dream_log:
            df = pd.DataFrame(st.session_state.dream_log)
            df = df.iloc[::-1]  # Legfrissebb felülre
            st.dataframe(df, width='stretch')
        else:
            st.info("A helyi napló még üres. Írd meg az első álmodat!")
       
# Kezdeti beolvasás az alkalmazás indításakor
if not st.session_state.dream_log:
    st.session_state.dream_log = load_dreams_from_local()
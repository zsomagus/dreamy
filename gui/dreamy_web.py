# app.py
# 🌙 Dreamy Widget - Streamlit Edition
# Futatás:
# streamlit run app.py

import os
import json
import pendulum
import streamlit as st
import pandas as pd

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

DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
OUTPUT_FOLDER = os.path.join(DOWNLOADS, "Álmaim")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

DREAM_LOG_FILE = os.path.join(OUTPUT_FOLDER, "dream_log.json")

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="Dreamy Widget",
    page_icon="🌙",
    layout="wide"
)

# --- PWA INTEGRÁCIÓ ÉS REGISZTRÁCIÓ ---
# Beágyazzuk a manifestet és elindítjuk a háttérben futó service workert
pwa_html = """
<link rel="manifest" href="/static/manifest.json">
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('/static/service_worker.js')
        .then(function(reg) { console.log('Service Worker sikeresen regisztrálva!', reg); })
        .catch(function(err) { console.error('Service Worker regisztrációs hiba:', err); });
    });
  }
</script>
"""
# Megjelenítjük láthatatlanul a komponenst a felületen
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
# SESSION STATE
# =========================================================

if "dream_log" not in st.session_state:
    st.session_state.dream_log = []

if "analysis_text" not in st.session_state:
    st.session_state.analysis_text = ""

if "music_prompt" not in st.session_state:
    st.session_state.music_prompt = ""

if "chart_path" not in st.session_state:
    st.session_state.chart_path = None

if "yantra_path" not in st.session_state:
    st.session_state.yantra_path = None


# =========================================================
# LOAD DREAM LOG
# =========================================================

if os.path.exists(DREAM_LOG_FILE):
    try:
        with open(DREAM_LOG_FILE, "r", encoding="utf-8") as f:
            st.session_state.dream_log = json.load(f)
    except:
        st.session_state.dream_log = []


# =========================================================
# LOAD DREAM DICTIONARY (JAVÍTVA)
# =========================================================# =========================================================
# LOAD DREAM DICTIONARY (VÉGLEGES JAVÍTÁS)
# =========================================================

# Mivel a script a 'dreamy' mappából fut, a __file__ mellé kell rakni a fájlt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALOMSZOTAR_PATH = os.path.join(BASE_DIR, "alomszotar.json")

# Kényszerített ellenőrzés: ha így sem látja, megnézzük a szülőmappát is
if not os.path.exists(ALOMSZOTAR_PATH):
    # Teszteljük, hogy egy mappával feljebb van-e
    ALOMSZOTAR_PATH = os.path.join(os.path.dirname(BASE_DIR), "alomszotar.json")

try:
    SZOTAR = load_alomszotar(ALOMSZOTAR_PATH)
    print(f"🎯 SIKERESEN BETÖLTVE: {ALOMSZOTAR_PATH}")
except Exception as e:
    st.error(f"Hiba az álomszótár betöltésekor: {e}")
    SZOTAR = {"alomszotar": []}
# =========================================================
# HELPERS
# =========================================================

def save_dreams():
    with open(DREAM_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            st.session_state.dream_log,
            f,
            ensure_ascii=False,
            indent=2
        )


def levag_ragokat(szo: str):

    ragok = [
        "ban", "ben", "val", "vel",
        "hoz", "hez", "höz",
        "nak", "nek",
        "ból", "ből",
        "ről", "tól", "től"
    ]

    for rag in ragok:
        if szo.lower().endswith(rag) and len(szo) > len(rag) + 2:
            return szo[:-len(rag)]

    return szo


def analyze_dream(text, keywords):

    talalatok = []
    szimbolumok = []

    szavak = [
        s.strip().lower()
        for s in text.split()
        if len(s.strip()) > 2
    ]

    szavak_tovei = [levag_ragokat(s) for s in szavak]

    egyedi_kulcsszavak = [
        k.strip().lower()
        for k in keywords.split(",")
        if k.strip()
    ]

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
        year=now.year,
        month=now.month,
        day=now.day,
        hour=now.hour,
        minute=now.minute,
        lat=lat,
        lon=lon,
        timezone_offset=now.utcoffset().total_seconds() / 3600,
        varga_label="D1 (Rashi)"
    )

    svg_res, png_res = draw.rajzol_del_indiai_horoszkop(
        planet_data=res["planet_data"],
        tithi=res["tithi"],
        horoszkop_nev=res["varga_code"]
    )

    raw_tithi = str(res.get("tithi", "13")).lower()

    tithi_szam = 13

    if "14" in raw_tithi:
        tithi_szam = 14
    elif "15" in raw_tithi:
        tithi_szam = 15
    elif "11" in raw_tithi:
        tithi_szam = 11
    elif "12" in raw_tithi:
        tithi_szam = 12

    yantra = astro_core.find_yantra_by_tithi(tithi_szam)

    return png_res, yantra


# =========================================================
# HEADER
# =========================================================

st.title("🌙 Dreamy Widget")
st.caption("Álomnapló • AI Prompt • Prashna • Yantra")


# =========================================================
# LAYOUT
# =========================================================

left_col, right_col = st.columns([1, 1])


# =========================================================
# LEFT
# =========================================================

with left_col:

    st.subheader("📝 Új álom")

    dream_text = st.text_area(
        "Mit álmodtál?",
        height=180
    )

    mood = st.selectbox(
        "Hangulat",
        [
            "Nyugodt",
            "Zaklatott",
            "Misztikus",
            "Félelmetes",
            "Boldog",
            "Zavaros",
            "Relaxált/Meditatív"
        ]
    )

    keywords = st.text_input(
        "Kulcsszavak (vesszővel)"
    )

    st.subheader("📍 Prashna koordináták")

    lat = st.number_input(
        "Szélesség",
        value=46.8572
    )

    lon = st.number_input(
        "Hosszúság",
        value=18.1533
    )

    if st.button("✨ Mentés és értelmezés"):

        if dream_text.strip():

            talalatok, szimbolumok = analyze_dream(
                dream_text,
                keywords
            )

            if talalatok:
                st.session_state.analysis_text = (
                    "🔮 Értelmezések\n\n"
                    + "\n".join(talalatok)
                )
            else:
                st.session_state.analysis_text = (
                    "❌ Nincs találat az álomszótárban."
                )

            prompt = build_music_prompt(
                dream_text,
                mood,
                keywords,
                szimbolumok
            )

            st.session_state.music_prompt = prompt

            now = pendulum.now("Europe/Budapest")

            entry = {
                "Dátum": now.format("YYYY-MM-DD HH:mm"),
                "Hangulat": mood,
                "Kulcsszavak": keywords,
                "Szimbolumok": szimbolumok,
                "Leírás": dream_text
            }

            st.session_state.dream_log.append(entry)

            save_dreams()

            # Horoszkóp
            try:

                chart_path, yantra_path = generate_prashna_chart(
                    lat,
                    lon
                )

                st.session_state.chart_path = chart_path
                st.session_state.yantra_path = yantra_path

            except Exception as e:
                st.error(f"Horoszkóp hiba: {e}")

            # Kotta export
            try:

                idokod = now.format("YYYYMMDD_HHmmss")

                export_score_to_pdf_and_png(
                    prompt,
                    OUTPUT_FOLDER,
                    f"kotta_prompt_{idokod}"
                )

            except Exception as e:
                st.warning(f"Kotta export hiba: {e}")

    st.subheader("🔮 Értelmezés")

    st.text_area(        
        "Értelmezés",
        value=st.session_state.analysis_text,
        height=260,
        label_visibility="collapsed"
    )
    st.subheader("🎵 AI Prompt")

    st.code(
        st.session_state.music_prompt,
        language="markdown"
    )


# =========================================================
# RIGHT
# =========================================================

with right_col:

    tabs = st.tabs([
        "📊 Prashna",
        "🔮 Yantra",
        "📜 Napló"
    ])

    # =====================================================
    # PRASHNA (JAVÍTVA a use_container_width figyelmeztetés)
    # =====================================================

    with tabs[0]:

        if st.session_state.chart_path and os.path.exists(
            st.session_state.chart_path
        ):

            st.image(
                st.session_state.chart_path,
                width="stretch"
            )
        else:
            st.info("Még nincs generált horoszkóp.")

    # =====================================================
    # YANTRA
    # =====================================================

    with tabs[1]:

        if st.session_state.yantra_path and os.path.exists(
            st.session_state.yantra_path
        ):

            st.image(
                st.session_state.yantra_path,
                width=500
            )
        else:
            st.info("Még nincs yantra.")

    # =====================================================
    # DREAM LOG
    # =====================================================

with tabs[2]:

    if st.session_state.dream_log:

        df = pd.DataFrame(
            list(reversed(st.session_state.dream_log))
        )

        # Javítás a vegyes típusú oszlopokra
        if "Szimbolumok" in df.columns:
            df["Szimbolumok"] = df["Szimbolumok"].apply(
                lambda x: ", ".join(x)
                if isinstance(x, list)
                else str(x)
            )

        if "Szimbólumok" in df.columns:
            df["Szimbólumok"] = df["Szimbólumok"].astype(str)

        st.dataframe(
            df,
            width="stretch"
        )
    else:
        st.info("Még nincs mentett álom.")
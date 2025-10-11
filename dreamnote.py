import streamlit as st
from datetime import datetime
import pandas as pd
from moulok import astro_core
# Inicializálás
st.set_page_config(page_title="Álomidéző Napló", page_icon="🌌", layout="centered")

st.title("🌙 Álomidéző Napló")
st.markdown("Jegyezd fel álmaidat, hangulataidat és szimbólumaidat – minden reggel egy új kapu a tudattalanhoz.")

# Álombejegyzés
st.header("📝 Új álom bejegyzése")

with st.form("dream_form"):
    dream_text = st.text_area("Mit álmodtál?", height=150)
    mood = st.selectbox("Milyen hangulatban volt az álom?", ["Nyugodt", "Zaklatott", "Misztikus", "Félelmetes", "Boldog", "Zavaros"])
    symbols = st.multiselect("Milyen szimbólumok jelentek meg?", ["Víz", "Kígyó", "Tükör", "Repülés", "Tűz", "Hold", "Ismeretlen személy"])
    submitted = st.form_submit_button("✨ Mentés")

# Adatmentés (egyszerűen session state-ben, később fájlba vagy adatbázisba is mehet)
if "dream_log" not in st.session_state:
    st.session_state.dream_log = []

if submitted and dream_text:
    st.session_state.dream_log.append({
        "Dátum": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Álom": dream_text,
        "Hangulat": mood,
        "Szimbólumok": ", ".join(symbols)
    })
    st.success("Álom mentve! 🌠")

# Archívum megjelenítése
st.header("📜 Korábbi álmok")

if st.session_state.dream_log:
    df = pd.DataFrame(st.session_state.dream_log)
    st.dataframe(df[::-1], use_container_width=True)
else:
    st.info("Még nincs elmentett álom. Kezdd el a naplózást!")


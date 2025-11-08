import streamlit as st
import pendulum
import pandas as pd
import os
import json
import shutil


# 🔄 __pycache__ törlése
def torol_pycache(gyoker="."):
    for root, dirs, files in os.walk(gyoker):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
                print(f"Törölve: {os.path.join(root, d)}")

torol_pycache("modulok")

# 💾 Álombejegyzések betöltése
if "dream_log" not in st.session_state:
    if os.path.exists("dream_log.json"):
        with open("dream_log.json", "r", encoding="utf-8") as f:
            st.session_state.dream_log = json.load(f)
    else:
        st.session_state.dream_log = []

# 🌌 UI beállítások
st.set_page_config(page_title="Álomidéző Napló", page_icon="🌌", layout="centered")
st.title("🌙 Álomidéző Napló")
st.markdown("Jegyezd fel álmaidat, hangulataidat és szimbólumaidat – minden reggel egy új kapu a tudattalanhoz.")

# 📝 Új álom bejegyzése
st.header("📝 Új álom bejegyzése")

with st.form("dream_form"):
    dream_text = st.text_area("Mit álmodtál?", height=150)
    mood = st.selectbox("Milyen hangulatban volt az álom?", ["Nyugodt", "Zaklatott", "Misztikus", "Félelmetes", "Boldog", "Zavaros"])
    symbols = st.multiselect("Milyen szimbólumok jelentek meg?", ["Víz", "Kígyó", "Tükör", "Repülés", "Tűz", "Hold", "Ismeretlen személy"])
    submitted = st.form_submit_button("✨ Mentés")

# 💾 Mentés pendulummba
if submitted and dream_text:
    now = pendulum.now("Europe/Budapest")
    datum_str = now.format("YYYY-MM-DD HH:mm")
    st.session_state.dream_log.append({
        "Dátum": datum_str,
        "Álom": dream_text,
        "Hangulat": mood,
        "Szimbólumok": ", ".join(symbols)
    })
    st.success("Álom mentve! 🌠")

    with open("dream_log.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.dream_log, f, ensure_ascii=False, indent=2)

# 📜 Archívum megjelenítése
st.header("📜 Korábbi álmok")
if st.session_state.dream_log:
    df = pd.DataFrame(st.session_state.dream_log)
    st.dataframe(df[::-1], use_container_width=True)
else:
    st.info("Még nincs elmentett álom. Kezdd el a naplózást!")
if submitted:
    st.session_state.dream_log.append({
        "text": dream_text,
        "mood": mood,
        "symbols": symbols,
        "timestamp": pendulum.now().to_iso8601_string()
    })

    st.success("Álom mentve!")

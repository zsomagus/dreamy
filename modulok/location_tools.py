import streamlit as st
from modulok.config import fill_coordinate_entries
st.subheader("📍 Prashna helyszín megadása")

with st.form("prashna_location_form"):
    prashna_city = st.text_input("Kérdés helyszíne (város)", value="Budapest")
    prashna_lat = st.text_input("Szélességi fok", value="")
    prashna_lon = st.text_input("Hosszúsági fok", value="")
    prashna_submit = st.form_submit_button("🔍 Mentés")

if prashna_submit:
    if not prashna_lat or not prashna_lon:
        lat, lon = get_coordinates(prashna_city)
        prashna_lat = prashna_lat or lat
        prashna_lon = prashna_lon or lon
    st.session_state.prashna_location = {
        "city": prashna_city,
        "latitude": prashna_lat,
        "longitude": prashna_lon
    }
    st.success(f"Prashna helyszín mentve: {prashna_city} ({prashna_lat}, {prashna_lon})")
st.subheader("🌍 Születési hely koordináta kereső")

with st.form("rashi_location_form"):
    rashi_city = st.text_input("Születési hely (város)", value="Budapest")
    keres_submit = st.form_submit_button("🔍 Keresés")

if keres_submit:
    lat, lon = get_coordinates(rashi_city)
    if lat and lon:
        st.session_state.rashi_location = {
            "city": rashi_city,
            "latitude": lat,
            "longitude": lon
        }
        st.success(f"Koordináták megtalálva: {lat}, {lon}")
    else:
        st.warning("Nem található koordináta ehhez a városhoz.")

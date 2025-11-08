import streamlit as st
import pendulum
import pandas as pd
import os
import json
import shutil
from modulok import astro_core, draw, prashna_core, varshaphala_tools, location_tools
from modulok.dasa_tools import calculate_dasa_info
from modulok import media_pipeline
from modulok.media_pipeline import generate_house_bundle


# 🔄 __pycache__ törlése
def torol_pycache(gyoker="."):
    for root, dirs, files in os.walk(gyoker):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
                print(f"Törölve: {os.path.join(root, d)}")

torol_pycache("modulok")

st.title("🎼 Sonic Jyotish – Házalapú archetípus generálás")

haz_szam = st.selectbox("Válassz házat", list(range(1, 13)))
if st.button("Generálás"):
    result = generate_house_bundle(haz_szam)
    st.subheader("📝 Spirituális tanítás prompt")
    st.text(result["prompt"])

    st.subheader("🎨 Képek")
    for img_path in result["images"]:
        st.image(img_path)

    st.subheader("🎶 MP3")
    audio_file = open(result["mp3"], "rb")
    st.audio(audio_file.read(), format="audio/mp3")

    st.subheader("🎼 Kotta PDF")
    with open(result["pdf"], "rb") as f:
        st.download_button("Letöltés", f, file_name="kotta.pdf")

st.header("🌟 Születési adatok megadása")

with st.form("birth_form"):
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("Születési dátum", value=pendulum.date(1500, 1, 1))
        birth_time = st.time_input("Születési idő", value=pendulum.time(12, 0))
    with col2:
        birth_place = st.text_input("Születési hely (város)", value="Budapest")
        latitude = st.text_input("Szélességi fok (pl. 47.4979)", value="")
        longitude = st.text_input("Hosszúsági fok (pl. 19.0402)", value="")

    submitted_birth = st.form_submit_button("🔍 Adatok mentése")

if submitted_birth:
    birth_dt = pendulum.datetime(
        birth_date.year, birth_date.month, birth_date.day,
        birth_time.hour, birth_time.minute,
        tz="Europe/Budapest"
    )
    st.session_state.birth_data = {
        "datetime": birth_dt.to_iso8601_string(),
        "place": birth_place,
        "latitude": latitude,
        "longitude": longitude
    }
    st.success("Születési adatok elmentve! 🌠")

with st.sidebar:
    st.header("🔮 Navigáció")

    választás = st.radio("Válassz modult:", [
        "Prashna – kérdezői horoszkóp",
        "Rashi – születési horoszkóp",
        "Varga – részhoroszkópok",
        "Yantra – tithi alapján",
        "Elemzés – bolygók, házak, karakterek",
        "Korszakrendszer – Vimshottari Dasa"
    ])

if választás == "Prashna – kérdezői horoszkóp":
    st.subheader("🕉️ Prashna horoszkóp")
    prashna_data = prashna_core.fill_prashna_data_streamlit()
    tithi = int(((prashna_data["chart_data"]["Moon"]["longitude"] - prashna_data["chart_data"]["Sun"]["longitude"]) % 360) / 12) + 1
    draw.rajzol_del_indiai_horoszkop(prashna_data["chart_data"], tithi, is_prashna=True, date_str=prashna_data["date"], time_str=prashna_data["time"])
    prashna_img_path = os.path.join("static", f"prashna_{prashna_data['date']}_{prashna_data['time'].replace(':', '-')}_D1.png")
    st.image(prashna_img_path, caption="Prashna Chart")
if st.button("🎼 Generálj zenét és képet az elemzésből", key="Prashna_generate"):
    elemzes = prashna_core.analyze_dream(dream_text, mood, symbols)
    prompt = prompt_from_analysis(elemzes)
    folder = create_output_folder(prompt)
    save_prompt(prompt, folder)
    mp3 = generate_mp3(prompt, folder)
    xml, midi = generate_musicxml(prompt, folder)
    pdf = export_pdf(xml, folder)
    image = generate_image(prompt, folder)

    st.success(f"Média generálva: {folder}")
    st.audio(mp3)
    st.image(image)

elif választás == "Rashi – születési horoszkóp":
    st.subheader("🌙 Rashi horoszkóp")
    # Példa születési dátum
    birth_dt = pendulum.datetime(1976, 3, 15, 21, 53, tz="Europe/Budapest")
    birth_data = astro_core.last_planet_positions(birth_dt)
    tithi_birth = int(((birth_data["Moon"]["longitude"] - birth_data["Sun"]["longitude"]) % 360) / 12) + 1
    draw.rajzol_del_indiai_horoszkop(birth_data, tithi_birth, horoszkop_nev="Rashi", vezeteknev="teszt", keresztnev="szülött")
    rashi_img_path = os.path.join("static", "teszt_szülött_horoszkop_Rashi.png")
    st.image(rashi_img_path, caption="Rashi Chart")
if st.button("🎼 Generálj zenét és képet az elemzésből", key="rashi_generate"):
    elemzes = astro_core.analyze_dream(dream_text, mood, symbols)
    prompt = prompt_from_analysis(elemzes)
    folder = create_output_folder(prompt)
    save_prompt(prompt, folder)
    mp3 = generate_mp3(prompt, folder)
    xml, midi = generate_musicxml(prompt, folder)
    pdf = export_pdf(xml, folder)
    image = generate_image(prompt, folder)

    st.success(f"Média generálva: {folder}")
    st.audio(mp3)
    st.image(image)

elif választás == "Varga – részhoroszkópok":
    st.subheader("📜 Varga rendszerek")
    for varga_nev in ["D9", "D10", "D60"]:
        varga_szorzo = varga_factors.get(varga_nev, 1)
        varga_positions = calculate_varga_positions(birth_data, varga_szorzo)
        varga_positions["ASC"] = birth_data["ASC"]
        draw.rajzol_del_indiai_horoszkop(varga_positions, tithi_birth, horoszkop_nev=varga_nev, vezeteknev="teszt", keresztnev="szülött")
        varga_img_path = os.path.join("static", f"teszt_szülött_horoszkop_{varga_nev}.png")
        st.image(varga_img_path, caption=f"{varga_nev} részhoroszkóp")
if st.button("🎼 Generálj zenét és képet az elemzésből", key="varga_generate"):
        elemzes = astro_core.analyze_dream(dream_text, mood, symbols)
        prompt = prompt_from_analysis(elemzes)
        folder = create_output_folder(prompt)
        save_prompt(prompt, folder)
        mp3 = generate_mp3(prompt, folder)
        xml, midi = generate_musicxml(prompt, folder)
        pdf = export_pdf(xml, folder)
        image = generate_image(prompt, folder)

        st.success(f"Média generálva: {folder}")
        st.audio(mp3)
        st.image(image)

elif választás == "Yantra – tithi alapján":
    st.subheader("🔍 Yantra keresés kulcsszavak alapján")

    # Yantra adatok betöltése
    try:
        with open("yantra_analysis.json", "r", encoding="utf-8") as f:
            yantra_list = json.load(f)
    except Exception as e:
        st.error(f"Hiba a yantra_analysis.json betöltésekor: {e}")
        yantra_list = []

    # Kulcsszavak kigyűjtése
    kulcsszavak = sorted({kw for y in yantra_list for kw in y.get("keywords", [])})
    választott_kulcsszó = st.selectbox("Válassz kulcsszót:", kulcsszavak)

    # Yantrák szűrése a kulcsszó alapján
    találatok = [y for y in yantra_list if választott_kulcsszó in y.get("keywords", [])]

    if találatok:
        for y in találatok:
            st.markdown(f"### 🧘 {y['name']}")
            yantra_path = os.path.join("static", "yantra", y["image"])
            if os.path.exists(yantra_path):
                st.image(yantra_path, caption=f"{y['name']} yantra", use_column_width=True)
            else:
                st.warning(f"Nincs kép a(z) {y['name']} yantrához.")
            st.markdown(f"**Leírás:** {y['description']}")
            st.markdown(f"**Mantra:** *{y['mantra']}*")
            st.markdown("**Kulcsszavak:** " + ", ".join(y["keywords"]))
            st.markdown("---")
    else:
        st.info("Nincs yantra ehhez a kulcsszóhoz.")

elif választás == "Elemzés – bolygók, házak, karakterek":
    st.subheader("🧠 Elemzés")
    for planet, data in birth_data.items():
        fok = round(data["longitude"] % 30, 2)
        jegy = data.get("sign", "Ismeretlen")
        ház = data.get("house", "?")
        st.markdown(f"**{planet}** – {fok}° ({jegy}), {ház}. ház")

elif választás == "Korszakrendszerek":
    st.subheader("🕰️ Dasa mandala – kozmikus időkerék")

    # Planet positions betöltése (pl. születési képletből vagy prashna_data-ból)
    positions = prashna_data["chart_data"]  # vagy birth_data, ha van

    # Mandala generálás
    from modulok.dasa_tools import calculate_dasa_info, interpret_dasa_trio
    dasa_info = calculate_dasa_info(positions)
    dasa_trio = {
        "maha": dasa_info["Mahadasa"]["planet"],
        "antara": dasa_info["Antardasa"]["planet"],
        "praty": dasa_info["Pratyantardasa"]["planet"],
    }

    interpretation = interpret_dasa_trio(positions, dasa_trio)
    st.markdown(f"**Aktuális daśa-trió:** {dasa_trio['maha']} / {dasa_trio['antara']} / {dasa_trio['praty']}")
    st.markdown(f"**Értelmezés:** {interpretation}")
    st.image(svg_path, caption="Dasa mandala (pillanatkép)", use_column_width=True)

def get_dasa_trio_for_dream(positions, datum_str):
    dt = pendulum.parse(datum_str, tz="Europe/Budapest")
    dasa_info = calculate_dasa_info(positions, start_year=dt.year)
    maha = dasa_info["Mahadasa"]["planet"][:2]
    antara = dasa_info["Antardasa"]["planet"][:2]
    praty = dasa_info["Pratyantardasa"]["planet"][:2]
    return f"{maha}/{antara}/{praty}"

with open("dream_log.json", "r", encoding="utf-8") as f:
    dreams = json.load(f)

álom_adatok = []
for álom in dreams:
    dátum = álom["Dátum"]
    korszak = get_dasa_trio_for_dream(prashna_data["chart_data"], dátum)
    álom_adatok.append({
        "Dátum": dátum,
        "Álom": álom["Álom"],
        "Hangulat": álom["Hangulat"],
        "Szimbólumok": álom["Szimbólumok"],
        "Daśa-trió": korszak
    })

df = pd.DataFrame(álom_adatok)
st.subheader("🌙 Álomnapló – daśa-trióval")
st.dataframe(df)

import os  # noqa: F401
import pendulum
from modulok.config import convert_to_utc
from modulok import tables
import swisseph as swe
import matplotlib.pyplot as plt
from PIL import Image  # noqa: F401
from modulok.tables import house_positions, varga_factors
from modulok.astro_core import calculate_ascendant, calculate_varga_positions, find_yantra_by_tithi, calculate_nakshatra


def rajzol_del_indiai_horoszkop(
    planet_data,
    tithi,
    horoszkop_nev="D1",
    date_str=None,
    time_str=None,
    vezeteknev=None,
    keresztnev=None,
    is_prashna=False,
):
    fig, ax = plt.subplots(figsize=(6, 6))

    # Háttérszín narancs
    fig.patch.set_facecolor("#FFA500")
    ax.set_facecolor("#FFA500")

    # Zöld rács – 12 ház, középső 4 mező kihagyva
    exclude_coords = [(1, 1), (2, 1), (1, 2), (2, 2)]
    for x in range(4):
        for y in range(4):
            if (x, y) not in exclude_coords:
                ax.plot([x, x + 1], [y, y], color="green", linewidth=2)
                ax.plot([x + 1, x + 1], [y, y + 1], color="green", linewidth=2)
                ax.plot([x + 1, x], [y + 1, y + 1], color="green", linewidth=2)
                ax.plot([x, x], [y + 1, y], color="green", linewidth=2)

    # Yantra beillesztése középre
    yantra_path = find_yantra_by_tithi(tithi)
    if yantra_path:
        try:
            yantra = Image.open(yantra_path).resize((150, 150))
            ax.imshow(yantra, extent=[1.0, 3.0, 1.0, 3.0])
        except Exception as e:
            print(f"Yantra megnyitási hiba: {e}")
    else:
        print(f"Nincs yantra fájl a(z) {tithi}. tithi-hez.")

    # Bolygók házba rendezése
    house_planets = {i: [] for i in range(1, 13)}
    for planet, data in planet_data.items():
        degrees = data["longitude"] % 360
        sign = int(degrees // 30) + 1
        abbreviation = tables.planet_abbreviations.get(planet, planet[:2].upper())
        house_planets[sign].append((planet, abbreviation))

    # Bolygók megjelenítése
    for hszam, (x, y) in tables.house_positions.items():
        bolygok = house_planets[hszam]
        for idx, (full_name, abbrev) in enumerate(bolygok):
            planet_deg = planet_data[full_name]["longitude"] % 30
            fok = int(planet_deg)
            perc = int((planet_deg - fok) * 60)
            label = f"{abbrev} {fok}° {perc}'"
            ax.text(
                x + 0.5,
                y + 0.8 - 0.25 * idx,
                label,
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold",
                color="black",
            )

    # ASC átló
    if "ASC" in planet_data:
        asc_deg = planet_data["ASC"]["longitude"] % 360
        asc_sign = int(asc_deg // 30) + 1
        if asc_sign in tables.house_positions:
            x, y = tables.house_positions[asc_sign]
            ax.plot([x, x + 1], [y, y + 1], color="red", linewidth=3)

    ax.set_title(
        f"Dél-indiai horoszkóp – {horoszkop_nev} – Tithi: {tithi}",
        fontsize=14,
        fontweight="bold",
    )

    # Mentés fájlba
    if is_prashna and date_str and time_str:
        datum = date_str.strip()
        ido = time_str.strip().replace(":", "-")
        filename = os.path.join("static", f"prashna_{datum}_{ido}_{horoszkop_nev}.png")
    elif vezeteknev and keresztnev:
        filename = os.path.join(
            "static",
            f"{vezeteknev.lower()}_{keresztnev.lower()}_horoszkop_{horoszkop_nev}.png",
        )
    else:
        filename = os.path.join("static", f"horoszkop_{horoszkop_nev}.png")

    plt.savefig(filename, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print(f"Mentve: {filename}")



def draw_chart_for_current_input(
    date_str,
    time_str,
    timezone_str,
    latitude_str,
    longitude_str,
    varga_nev,
    vezeteknev,
    keresztnev,
    is_prashna=False,
):
    # 🕰️ Pendulum: időpont létrehozása és UTC-re konvertálás
    local_dt = pendulum.parse(f"{date_str}T{time_str}", tz=timezone_str)
    utc_dt = local_dt.in_timezone("UTC")

    # 📅 Julian Day számítás
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

    planet_data = {}
    for name, pid in tables.planet_ids.items():
        pos, _ = swe.calc_ut(jd_ut, pid)
        sidereal_pos = (pos[0] - ayanamsa) % 360
        planet_data[name] = {"longitude": sidereal_pos}

    tithi = (
        int(
            ((planet_data["Moon"]["longitude"] - planet_data["Sun"]["longitude"]) % 360)
            / 12
        )
        + 1
    )

    planet_data["ASC"] = {"longitude": asc_sidereal}
    rajzol_del_indiai_horoszkop(
        planet_data,
        tithi,
        horoszkop_nev="D1",
        date_str=date_str,
        time_str=time_str,
        vezeteknev=vezeteknev,
        keresztnev=keresztnev,
        is_prashna=is_prashna,
    )

    varga_szorzo = tables.varga_factors.get(varga_nev, 1)
    if varga_szorzo > 1:
        varga_positions = calculate_varga_positions(planet_data, varga_szorzo)
        varga_positions["ASC"] = {"longitude": asc_sidereal}
        rajzol_del_indiai_horoszkop(
            varga_positions,
            tithi,
            horoszkop_nev=varga_nev.replace(" ", "_"),
            date_str=date_str,
            time_str=time_str,
            vezeteknev=vezeteknev,
            keresztnev=keresztnev,
        )

    messagebox.showinfo("Siker", "A horoszkópok elmentve képként!")


def show_horoszkop_image(vezeteknev, keresztnev, varga="D1"):
    filename = f"{vezeteknev.lower()}_{keresztnev.lower()}_horoszkop_{varga}.png"
    filepath = os.path.join("static", filename)
    if os.path.exists(filepath):
        image = Image.open(filepath)
        st.image(image, caption=f"🖼️ Horoszkóp – {varga}", use_column_width=True)
    else:
        st.warning("A horoszkóp kép nem található.")

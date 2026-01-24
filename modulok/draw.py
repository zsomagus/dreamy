import matplotlib.pyplot as plt
from PIL import Image
from PyQt5.QtGui import QPixmap
from io import BytesIO
from modulok import tables
from modulok.astro_core import find_yantra_by_tithi


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
    fig, ax = plt.subplots(figsize=(20, 20))

    # Háttérszín
    fig.patch.set_facecolor("#FFA500")
    ax.set_facecolor("#FFA500")

    # Dél-indiai rács
    exclude_coords = [(1, 1), (2, 1), (1, 2), (2, 2)]
    for x in range(4):
        for y in range(4):
            if (x, y) not in exclude_coords:
                ax.plot([x, x + 1], [y, y], color="green", linewidth=2)
                ax.plot([x + 1, x + 1], [y, y + 1], color="green", linewidth=2)
                ax.plot([x + 1, x], [y + 1, y + 1], color="green", linewidth=2)
                ax.plot([x, x], [y + 1, y], color="green", linewidth=2)

    # Yantra középen
    yantra_path = find_yantra_by_tithi(tithi)
    if yantra_path:
        try:
            yantra = Image.open(yantra_path).resize((150, 150))
            ax.imshow(yantra, extent=[1.0, 3.0, 1.0, 3.0])
        except Exception as e:
            print("Yantra hiba:", e)

    # Bolygók házakba rendezése
    house_planets = {i: [] for i in range(1, 13)}
    for planet, data in planet_data.items():
        degrees = data["longitude"] % 360
        sign = int(degrees // 30) + 1
        abbrev = tables.planet_abbreviations.get(planet, planet[:2].upper())
        house_planets[sign].append((planet, abbrev))

    # Bolygók kiírása
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
                fontsize=45,
                fontweight="bold",
                color="black",
            )

    # ASC jelölése
    if "ASC" in planet_data:
        asc_deg = planet_data["ASC"]["longitude"] % 360
        asc_sign = int(asc_deg // 30) + 1
        if asc_sign in tables.house_positions:
            x, y = tables.house_positions[asc_sign]
            ax.plot([x, x + 1], [y, y + 1], color="red", linewidth=3)

    ax.set_title(
        f"Dél-indiai horoszkóp – {horoszkop_nev} – Tithi: {tithi}",
        fontsize=40,
        fontweight="bold",
    )

    # --- Pixmap visszaadása fájlmentés helyett ---
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=150, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close()

    pixmap = QPixmap()
    pixmap.loadFromData(buf.getvalue())
    return pixmap

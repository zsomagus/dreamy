# modulok/draw.py
import os
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

    # Háttérszín beállítása
    fig.patch.set_facecolor("#FFA500")
    ax.set_facecolor("#FFA500")

    # FIX TENGELYEK: Megfordítjuk az Y tengelyt, hogy a (0,3) a bal felső sarok legyen
    ax.set_xlim(0, 4)
    ax.set_ylim(4, 0)  
    ax.axis("off")

    # Dél-indiai rács megrajzolása (Vastag zöld vonalak)
    exclude_coords = [(1, 1), (2, 1), (1, 2), (2, 2)]
    for x in range(4):
        for y in range(4):
            if (x, y) not in exclude_coords:
                ax.plot([x, x + 1], [y, y], color="green", linewidth=4)
                ax.plot([x + 1, x + 1], [y, y + 1], color="green", linewidth=4)
                ax.plot([x + 1, x], [y + 1, y + 1], color="green", linewidth=4)
                ax.plot([x, x], [y + 1, y], color="green", linewidth=4)

    # ─── 1. YANTRA BEILLESZTÉSE ───
    # Dinamikusan megkeressük a Tithihez tartozó yantra képét az astro_core segítségével
    from modulok.astro_core import find_yantra_by_tithi
    yantra_path = find_yantra_by_tithi(tithi)
    if yantra_path and os.path.exists(yantra_path):
        try:
            yantra_img = Image.open(yantra_path)
            ax.imshow(yantra_img, extent=[1.005, 2.995, 2.995, 1.005], zorder=1)
        except Exception:
            pass

    # ─── 2. AYANAMSA MEGHATÁROZÁSA ───
    ayanamsa = 24.24  # Gyári fallback érték 2026-ra
    if isinstance(planet_data, dict) and "ayanamsa" in planet_data:
        ayanamsa = planet_data["ayanamsa"]

    # ─── 3. BOLYGÓK HÁZAKBA RENDEZÉSE VÉDIKUS POZÍCIÓ ALAPJÁN ───
    house_planets = {i: [] for i in range(1, 13)}
    ervenyes_bolygok = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for planet in planet_data:
        if planet in ervenyes_bolygok:
            # Megbízható adatkinyerés: támogatja a szótár (dict) és az objektum struktúrát is
            p_info = planet_data[planet]
            if isinstance(p_info, dict):
                tropical_lon = p_info.get("longitude", 0.0)
            else:
                tropical_lon = getattr(p_info, "longitude", 0.0)
            
            # Levonjuk az ayanamsát a sziderikus (védikus) zodiákushoz
            sidereal_lon = (tropical_lon - ayanamsa) % 360

            # Kiszámoljuk, melyik jegybe esik (1 = Kos, 2 = Bika ... 12 = Halak)
            sign = int(sidereal_lon // 30) + 1

            abbrev = tables.planet_abbreviations.get(planet, planet[:2].upper())
            house_planets[sign].append((planet, abbrev, sidereal_lon % 30))

    # ─── 4. BOLYGÓK RAJZOLÁSA (Maximálisan scannálható elrendezés) ───
    for hszam, (x, y) in tables.house_positions.items():
        bolygok = house_planets[hszam]

        for idx, (full_name, abbrev, rasi_deg) in enumerate(bolygok):
            fok = int(rasi_deg)
            perc = int((rasi_deg - fok) * 60)
            label = f"{abbrev} {fok}°{perc}'"

            # 2 oszlopos rendezés a cellákon belül, hogy ne fedjék le egymást
            col = idx % 2
            row = idx // 2

            x_pos = x + 0.26 + (col * 0.48)
            y_pos = y + 0.22 + (row * 0.16)

            ax.text(
                x_pos,
                y_pos,
                label,
                ha="center",
                va="center",
                fontsize=16,
                fontweight="bold",
                color="black",
            )

    # ─── 5. ASZCENDENS (ASC) KIRAJZOLÁSA VÉDIKUS HELYZET ALAPJÁN ───
    if "ASC" in planet_data:
        p_info = planet_data["ASC"]
        asc_tropical = p_info.get("longitude", 0.0) if isinstance(p_info, dict) else getattr(p_info, "longitude", 0.0)
        
        asc_sidereal = (asc_tropical - ayanamsa) % 360
        asc_sign = int(asc_sidereal // 30) + 1

        if asc_sign in tables.house_positions:
            ax_x, ax_y = tables.house_positions[asc_sign]
            ax.plot([ax_x, ax_x + 1], [ax_y, ax_y + 1], color="red", linewidth=2.5, linestyle="--")
            ax.text(ax_x + 0.15, ax_y + 0.25, "Asc", color="red", fontsize=14, fontweight="bold")

    # Pufferbe mentés és visszaadás a GUI-nak
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=100, facecolor=fig.get_facecolor())
    buf.seek(0)
    plt.close()

    pixmap = QPixmap()
    pixmap.loadFromData(buf.getvalue(), "PNG")
    return pixmap
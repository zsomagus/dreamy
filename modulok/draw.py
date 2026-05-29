# modulok/draw.py
import os
import matplotlib.pyplot as plt
from modulok import tables

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
    # Visszaállítjuk a hatalmas 20x20-as méretet a szép nagy betűkhöz!
    fig, ax = plt.subplots(figsize=(20, 20))

    fig.patch.set_facecolor("#FFA500")
    ax.set_facecolor("#FFA500")

    ax.set_xlim(0, 4)
    ax.set_ylim(4, 0)  
    ax.axis("off")

    # Dél-indiai rács megrajzolása (Vastag zöld vonalak)
    exclude_coords = [(1, 1), (2, 1), (1, 2), (2, 2)]
    for x in range(4):
        for y in range(4):
            if (x, y) not in exclude_coords:
                ax.plot([x, x + 1], [y, y], color="green", linewidth=5, zorder=2)
                ax.plot([x + 1, x + 1], [y, y + 1], color="green", linewidth=5, zorder=2)
                ax.plot([x + 1, x], [y + 1, y + 1], color="green", linewidth=5, zorder=2)
                ax.plot([x, x], [y + 1, y], color="green", linewidth=5, zorder=2)

    # ─── JEGYEK NEVEINEK KIÍRÁSA NAGY BETŰKKEL ───
    fallbacks = {1:"Kos", 2:"Bika", 3:"Ikrek", 4:"Rák", 5:"Oroszlán", 6:"Szűz", 
                 7:"Mérleg", 8:"Skorpió", 9:"Nyilas", 10:"Bak", 11:"Vízöntő", 12:"Halak"}

    for house_num, (x, y) in tables.house_positions.items():
        hu_name = fallbacks.get(house_num, "")
        ax.text(
            x + 0.05, y + 0.15, hu_name, 
            color="#444444", fontsize=20, fontweight="bold", zorder=3
        )

    # ─── BOLYGÓK HÁZAKBA RENDEZÉSE ───
    house_planets = {i: [] for i in range(1, 13)}
    ervenyes_bolygok = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for planet in planet_data:
        if planet in ervenyes_bolygok:
            p_info = planet_data[planet]
            v_lon = p_info.get("vedic_longitude", 0.0)
            sign = int(v_lon // 30) + 1
            abbrev = tables.planet_abbreviations.get(planet, planet[:2].upper())
            house_planets[sign].append((planet, abbrev, v_lon % 30))

    # ─── BOLYGÓK TÁGAS, NAGY BETŰS RAJZOLÁSA ───
    for hszam, (x, y) in tables.house_positions.items():
        bolygok = house_planets[hszam]
        for idx, (full_name, abbrev, rasi_deg) in enumerate(bolygok):
            fok = int(rasi_deg)
            perc = int((rasi_deg - fok) * 60)
            label = f"{abbrev} {fok}°{perc}'"

            col = idx % 2
            row = idx // 2
            x_pos = x + 0.28 + (col * 0.44)
            y_pos = y + 0.42 + (row * 0.24)

            ax.text(
                x_pos, y_pos, label,
                ha="center", va="center",
                fontsize=24, fontweight="bold", color="black",
                zorder=10
            )

    # ─── ASZCENDENS (ASC) KIRAJZOLÁSA VASTAG ÁTLÓVAL ───
    if "ASC" in planet_data:
        p_info = planet_data["ASC"]
        asc_lon = p_info.get("vedic_longitude", 0.0)
        asc_sign = int(asc_lon // 30) + 1
        rasi_deg = p_info.get("rasi_deg", 0.0)
        
        fok = int(rasi_deg)
        perc = int((rasi_deg - fok) * 60)

        if asc_sign in tables.house_positions:
            ax_x, ax_y = tables.house_positions[asc_sign]
            ax.plot([ax_x, ax_x + 1], [ax_y, ax_y + 1], color="red", linewidth=6, zorder=12)
            ax.text(
                ax_x + 0.12, ax_y + 0.38, f"Asc {fok}°{perc}'", 
                color="red", fontsize=24, fontweight="bold", zorder=13
            )

    # Biztonságos mentés tight-tal, hogy a betűk hatalmasak maradjanak
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    png_path = os.path.join(output_dir, f"prashna_{horoszkop_nev}.png")
    svg_path = os.path.join(output_dir, f"prashna_{horoszkop_nev}.svg")

    plt.savefig(png_path, format="png", bbox_inches="tight", dpi=100, facecolor=fig.get_facecolor())
    plt.savefig(svg_path, format="svg", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()

    return svg_path, png_path
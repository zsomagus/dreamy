import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pendulum
import numpy as np
import svgwrite
import pandas as pd
import math
from modulok import config
from modulok import prashna_core, astro_core
from modulok.dasa_tools import calculate_dasa_info, generate_dasa_summary

# Bolygók és színek
planets = ["Ket", "Ven", "Sun", "Moon", "Mars", "Rah", "Jup", "Sat", "Merc"]
colors = ["#8E44AD", "#E91E63", "#F39C12", "#3498DB", "#E74C3C", "#2C3E50", "#27AE60", "#7F8C8D", "#1ABC9C"]

# SVG szelet kirajzolása
def draw_ring_svg(dwg, center, radius, rotation_offset, label):
    for i, (planet, color) in enumerate(zip(planets, colors)):
        start_angle = i * 40 + rotation_offset
        end_angle = start_angle + 40

        # Szög radiánban
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        # Pontok kiszámítása
        x1 = center[0] + radius * math.cos(start_rad)
        y1 = center[1] + radius * math.sin(start_rad)
        x2 = center[0] + radius * math.cos(end_rad)
        y2 = center[1] + radius * math.sin(end_rad)

        path = dwg.path(d=f"M {center[0]},{center[1]} L {x1},{y1} A {radius},{radius} 0 0,1 {x2},{y2} Z",
                        fill=color, stroke="white", stroke_width=1)
        dwg.add(path)

        # Felirat
        mid_angle = (start_angle + end_angle) / 2
        mid_rad = math.radians(mid_angle)
        text_x = center[0] + (radius - 20) * math.cos(mid_rad)
        text_y = center[1] + (radius - 20) * math.sin(mid_rad)
        dwg.add(dwg.text(planet, insert=(text_x, text_y), text_anchor="middle",
                         font_size="10px", fill="white"))

# SVG generálás
def generate_mandala_svg(dasa_trio, chart_data, interpretation, summary_text):
    now = pendulum.now("Europe/Budapest")
    maha_angle = (now.hour % 24) * 15
    antara_angle = (now.minute % 60) * 6
    praty_angle = (now.second % 60) * 6

    dwg = svgwrite.Drawing("static/dasa_mandala.svg", size=("600px", "600px"))
    center = (300, 300)

    draw_ring_svg(dwg, center, 200, maha_angle, "Mahadasa")
    draw_ring_svg(dwg, center, 140, antara_angle, "Antardasa")
    draw_ring_svg(dwg, center, 80, praty_angle, "Pratyantardasa")

    # Feliratok
    dwg.add(dwg.text(dasa_trio["maha"], insert=(300, 40), text_anchor="middle", font_size="18px", fill="black"))
    dwg.add(dwg.text(interpretation, insert=(300, 560), text_anchor="middle", font_size="14px", fill="black"))

    dwg.save()

# Mandala generálás pozíciók alapján
def generate_mandala_for_positions(positions, start_year=None):
    dasa_info = calculate_dasa_info(positions, start_year)
    dasa_trio = {
        "maha": dasa_info["Mahadasa"]["planet"],
        "antara": dasa_info["Antardasa"]["planet"],
        "praty": dasa_info["Pratyantardasa"]["planet"],
    }

    interpretation = interpret_dasa_trio(positions, dasa_trio)
    summary_text = generate_dasa_summary(positions)
    generate_mandala_svg(dasa_trio, positions, interpretation, summary_text)

    return "static/dasa_mandala.svg", dasa_trio, interpretation

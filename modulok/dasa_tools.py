DASA_YEARS = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

NAKSHATRA_ORDER = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
]


def calculate_dasa_info(positions, start_year=None):
    """Egyszerű Vimshottari Dasa számítás positions dict alapján."""
    from datetime import datetime  # noqa: F401

    moon_lon = positions["Moon"]["longitude"]
    nakshatra_index = int((moon_lon % 360) // (360 / 27))
    starting_planet = NAKSHATRA_ORDER[nakshatra_index % 9]

    portion_in_nakshatra = (moon_lon % (360 / 27)) / (360 / 27)
    remaining_years = DASA_YEARS[starting_planet] * (1 - portion_in_nakshatra)

    current_year = start_year if start_year else datetime.now().year

    mahadasa = {
        "planet": starting_planet,
        "start": current_year,
        "end": round(current_year + remaining_years, 2)
    }

    antardasa_planet = NAKSHATRA_ORDER[0]
    antardasa = {
        "planet": antardasa_planet,
        "start": current_year,
        "end": round(
            current_year
            + (DASA_YEARS[starting_planet] * (DASA_YEARS[antardasa_planet] / 120)),
            2,
        )
    }

    pratyantardasa_planet = NAKSHATRA_ORDER[0]
    pratyantardasa = {
        "planet": pratyantardasa_planet,
        "start": current_year,
        "end": round(
            current_year
            + (
                DASA_YEARS[starting_planet]
                * (DASA_YEARS[antardasa_planet] / 120)
                * (DASA_YEARS[pratyantardasa_planet] / 120)
            ),
            2,
        ),
    }

    return {
        "Mahadasa": mahadasa,
        "Antardasa": antardasa,
        "Pratyantardasa": pratyantardasa,
    }
# modulok/dasa_analysis.py
def generate_dasa_summary(birth_data, calculate_dasa):
    # Pl. Vimsottari daśa kiszámítása
    dasa_list = calculate_dasa(birth_data)
    md = "## 🕰️ Daśa ciklusok\n\n"
    for dasa in dasa_list:
        md += f"- **{dasa['planet']}**: {dasa['start']} → {dasa['end']}\n"
    return md
    
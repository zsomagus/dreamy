import pendulum
import swisseph as swe
from modulok.tables import planet_ids
from modulok.astro_core import calculate_ascendant

def fill_prashna_data_with_coords(lat, lon):
    now = pendulum.now("Europe/Budapest")

    date_str = now.format("YYYY-MM-DD")
    time_str = now.format("HH:mm")

    utc_dt = now.in_timezone("UTC")
    jd_ut = swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60 + utc_dt.second / 3600,
    )

    ayanamsa = swe.get_ayanamsa_ut(jd_ut)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    asc_deg = calculate_ascendant(jd_ut, lat, lon)
    asc_sidereal = (asc_deg - ayanamsa) % 360

    chart_data = {}
    for name, pid in planet_ids.items():
        pos, _ = swe.calc_ut(jd_ut, pid)
        sidereal_pos = (pos[0] - ayanamsa) % 360
        chart_data[name] = {"longitude": sidereal_pos}

    chart_data["ASC"] = {"longitude": asc_sidereal}

    return {
        "date": date_str,
        "time": time_str,
        "chart_data": chart_data,
    }

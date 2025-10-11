import pendulum
from modulok.astro_core import get_planet_data

def fill_prashna_data_streamlit():
    now = pendulum.now("Europe/Budapest")

    # Alapértelmezett értékek
    date_str = now.format("YYYY-MM-DD")
    time_str = now.format("HH:mm")
    lat = "47.4979"
    lon = "19.0402"
    tz = "Europe/Budapest"
    dst = bool(now.dst())

    # UTC idő kiszámítása
    utc_dt = now.in_timezone("UTC")
    utc_str = utc_dt.format("YYYY-MM-DD HH:mm")

    # Planet data lekérése
    chart_data = get_planet_data(
        date=date_str,
        time=time_str,
        latitude=lat,
        longitude=lon,
        timezone=tz
    )

    return {
        "date": date_str,
        "time": time_str,
        "latitude": lat,
        "longitude": lon,
        "timezone": tz,
        "utc": utc_str,
        "dst": dst,
        "chart_data": chart_data
    }

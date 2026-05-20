import pendulum
from modulok import prashna_core
from modulok.draw import rajzol_del_indiai_horoszkop


def generate_prashna_pixmap(latitude: float, longitude: float):
    """
    Prashna horoszkóp számítása + pixmap generálása.
    A GUI csak ezt hívja meg.
    """

    prashna = prashna_core.fill_prashna_data_with_coords(latitude, longitude)
    planet_data = prashna["chart_data"]

    moon_lon = planet_data["Moon"]["longitude"]
    sun_lon = planet_data["Sun"]["longitude"]
    tithi = int(((moon_lon - sun_lon) % 360) / 12) + 1

    pixmap = rajzol_del_indiai_horoszkop(
        planet_data,
        tithi,
        horoszkop_nev="D1",
        date_str=prashna["date"],
        time_str=prashna["time"],
        is_prashna=True,
    )

    return pixmap
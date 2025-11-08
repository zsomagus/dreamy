import pendulum
import swisseph as swe
from modulok import astro_core


def calculate_solar_return_jd(date_str, time_str, lat, lon, tz, szul_utc: pendulum.DateTime, eletkor: int):
    """
    Szolár visszatérés (Varshaphala) Julian Day és időpont számítása.
    
    :param szul_utc: születési idő (UTC, pendulum DateTime)
    :param eletkor: életkor (év)
    :return: (best_jd, best_dt) → legjobb Julian Day és pendulum DateTime
    """
    # 🕰️ Julian Day a születési időpontra
    jd_szul = swe.julday(
        szul_utc.year,
        szul_utc.month,
        szul_utc.day,
        szul_utc.hour + szul_utc.minute / 60.0 + szul_utc.second / 3600.0,
    )

    # 🎯 Célév: születési év + életkor
    try:
        kb_return = szul_utc.replace(year=szul_utc.year + eletkor)
    except ValueError:
        # szökőnap hibákra: ha pl. feb 29 → feb 28
        kb_return = pendulum.datetime(
            szul_utc.year + eletkor,
            min(szul_utc.month, 2),
            min(szul_utc.day, 28),
            szul_utc.hour,
            szul_utc.minute,
            szul_utc.second,
            tz=szul_utc.timezone,
        )

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    nap_pos, _ = swe.calc_ut(jd_szul, swe.SUN)
    nap_fok = nap_pos[0]

    best_diff = 999
    best_jd = None
    best_dt = None

    # 🔍 Keresés ±72 órán belül, 30 perces lépésekben
    for minute_shift in range(-72 * 60, 72 * 60, 30):
        keresett = kb_return.add(minutes=minute_shift)
        jd_keresett = swe.julday(
            keresett.year,
            keresett.month,
            keresett.day,
            keresett.hour + keresett.minute / 60.0 + keresett.second / 3600.0,
        )
        pos, _ = swe.calc_ut(jd_keresett, swe.SUN)
        eltérés = abs((pos[0] - nap_fok + 180) % 360 - 180)
        if eltérés < best_diff:
            best_diff = eltérés
            best_jd = jd_keresett
            best_dt = keresett

    return best_jd, best_dt
# 3️⃣ Astro_core: képlet generálása
    chart_data = astro_core.get_planet_data(
        date=date_str,
        time=time_str,
        latitude=lat,
        longitude=lon,
        timezone=tz
    )
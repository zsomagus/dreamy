import logging
import re
from pathlib import Path
import pandas as pd
import swisseph as swe
import pendulum  # ⏳ új: pendulum a datetime helyett
# Alap elérési utak
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

YANTRA_PATH = STATIC_DIR / "yantra"

# Swiss Ephemeris elérési út
swe.set_ephe_path(str(STATIC_DIR / "ephe"))

# -----------------------------
# Időzóna / UTC utilok Pendulum-mal
# -----------------------------

def convert_to_utc(date_str: str, time_str: str, tz_str: str) -> pendulum.DateTime:
    """
    Helyi idő + időzóna → UTC (pendulum).
    """
    try:
        dt = pendulum.from_format(f"{date_str} {time_str}", "YYYY-MM-DD HH:mm", tz=tz_str)
        return dt.in_timezone("UTC")
    except Exception as e:
        logger.error(f"Hiba UTC konverziónál: {e}")
        raise

def is_dst_active(dt: pendulum.DateTime, timezone_str: str) -> bool:
    tz = pendulum.timezone(timezone_str)
    localized = dt.in_timezone(tz)
    return localized.dst().total_seconds() > 0

# -----------------------------
# GUI helper függvények
# -----------------------------
def set_dst_flag(var, timezone_str: str = "Europe/Budapest", dt: pendulum.DateTime | None = None) -> None:
    """Nyári időszámítás állapot beállítása GUI változóra."""
    dt = dt or pendulum.now()
    var.set(is_dst_active(dt, timezone_str))


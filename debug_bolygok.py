# debug_bolygok.py - futtasd egyszer
from modulok.astro_core import get_varga_chart_data
import pendulum

now = pendulum.now("Europe/Budapest")
res = get_varga_chart_data(
    year=now.year, month=now.month, day=now.day,
    hour=now.hour, minute=now.minute,
    lat=47.3, lon=18.15,
    timezone_offset=2.0,
    varga_label="D1 (Rashi)"
)
for k, v in res["planet_data"].items():
    print(f"  {k!r}: {v}")
# main.py

import subprocess
import sys
from pathlib import Path

app_file = Path(__file__).parent / "gui" / "dreamy_web.py"

subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    str(app_file)
])
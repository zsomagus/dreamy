import os
import traceback
import importlib.util
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

EXCLUDE_DIRS = {".ipynb_checkpoints", "__pycache__", "venv", ".git"}

def check_python_modules(base_dirs):
    print("🔍 Import‑ellenőrzés indul...\n")
    for directory in base_dirs:
        print(f"📂 Könyvtár: {directory}")
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for file in files:
                if file.endswith(".py") and "-checkpoint" not in file:
                    filepath = os.path.join(root, file)
                    relpath = os.path.relpath(filepath, ".")
                    modulename = relpath.replace(os.sep, ".").replace(".py", "")

                    try:
                        spec = importlib.util.spec_from_file_location(modulename, filepath)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        print(f"✅ Sikeres import: {modulename}")
                    except Exception:
                        print(f"❌ Hiba a modulban: {modulename}")
                        print(traceback.format_exc())
        print()

if __name__ == "__main__":
    # csak a gui és modulok mappát ellenőrizzük
    check_python_modules(["gui", "modulok"])

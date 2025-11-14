import os
import pendulum
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from modulok import dasa_mandala

class DasaWidget(QWidget):
    def __init__(self, planet_positions: dict):
        super().__init__()
        self.planet_positions = planet_positions
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.generateButton = QPushButton("🌀 Dasa mandala generálása")
        self.resultArea = QTextEdit()
        self.mandalaImage = QLabel()

        layout.addWidget(self.generateButton)
        layout.addWidget(self.resultArea)
        layout.addWidget(self.mandalaImage)

        self.setLayout(layout)
        self.generateButton.clicked.connect(self.generate_mandala)

    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "SonicJyotish")
        os.makedirs(folder, exist_ok=True)
        return folder

    def generate_mandala(self):
        svg_path, dasa_trio, interpretation = dasa_mandala.generate_mandala_for_positions(self.planet_positions)

        # Áthelyezés a Letöltések/SonicJyotish mappába
        output_folder = self.get_output_folder()
        final_svg = os.path.join(output_folder, "dasa_mandala.svg")
        os.replace(svg_path, final_svg)

        # Ha van PNG konverzió, itt tölthető be
        png_path = final_svg.replace(".svg", ".png")
        if os.path.exists(png_path):
            self.mandalaImage.setPixmap(QPixmap(png_path))

        # Szöveges eredmény
        self.resultArea.setText(
            f"🌙 Mahadasa: {dasa_trio['maha']}\n"
            f"🌿 Antardasa: {dasa_trio['antara']}\n"
            f"🌾 Pratyantardasa: {dasa_trio['praty']}\n\n"
            f"🧠 Értelmezés:\n{interpretation}\n\n"
            f"📁 Mentve: {final_svg}"
        )

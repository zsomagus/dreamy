import os
import pendulum
import swisseph as swe
import pyttsx3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument, QPixmap
from PyQt5.QtWidgets import QLabel

from modulok.astro_core import get_planet_data
from modulok import draw, audio_kotta_tools

class PrashnaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Alapértelmezett koordináták
        self.city = QLineEdit("Budapest")
        self.lat = QLineEdit("47.4979")
        self.lon = QLineEdit("19.0402")

        # Gombok
        self.calcButton = QPushButton("🔍 Prashna számítása")
        self.musicButton = QPushButton("🎵 Megzenésítés")
        self.savePDF = QPushButton("📄 Mentés PDF-be")
        self.readAloud = QPushButton("🔊 Felolvasás")

        # Eredmény és kép
        self.resultArea = QTextEdit()
        self.chartImage = QLabel()

        # Layout
        layout.addWidget(QLabel("Kérdés helyszíne"))
        layout.addWidget(self.city)
        layout.addWidget(QLabel("Szélességi fok"))
        layout.addWidget(self.lat)
        layout.addWidget(QLabel("Hosszúsági fok"))
        layout.addWidget(self.lon)
        layout.addWidget(self.calcButton)
        layout.addWidget(self.musicButton)
        layout.addWidget(self.savePDF)
        layout.addWidget(self.readAloud)
        layout.addWidget(self.resultArea)
        layout.addWidget(self.chartImage)

        self.setLayout(layout)

        # Gombok összekötése
        self.calcButton.clicked.connect(self.calculate_prashna)
        self.musicButton.clicked.connect(self.musicalize)
        self.savePDF.clicked.connect(self.save_pdf)
        self.readAloud.clicked.connect(self.read_text)

    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "SonicJyotish")
        os.makedirs(folder, exist_ok=True)
        return folder

    def calculate_prashna(self):
        now = pendulum.now("Europe/Budapest")
        date_str = now.format("YYYY-MM-DD")
        time_str = now.format("HH:mm")
        lat = float(self.lat.text())
        lon = float(self.lon.text())

        jd = swe.julday(
            now.year,
            now.month,
            now.day,
            now.hour + now.minute / 60.0 + now.second / 3600.0,
        )

        chart_data = get_planet_data(jd=jd, latitude=lat, longitude=lon)

        draw.rajzol_del_indiai_horoszkop(
            chart_data,
            tithi=1,
            horoszkop_nev="Prashna",
            date_str=date_str,
            time_str=time_str,
            vezeteknev="user",
            keresztnev="prashna",
            is_prashna=True
        )

        path = os.path.join(self.get_output_folder(), f"prashna_{date_str}_{time_str.replace(':', '-')}_Prashna.png")
        self.chartImage.setPixmap(QPixmap(path))
        self.resultArea.setText(f"📍 Prashna képlet kiszámítva:\n{date_str} {time_str}\nKép mentve: {path}")

    def musicalize(self):
        text = self.resultArea.toPlainText()
        mix, sr = audio_kotta_tools.text_to_music(text)
        path = os.path.join(self.get_output_folder(), "prashna_zene.wav")
        audio_kotta_tools.write(path, sr, mix)
        self.resultArea.append(f"🎵 Zene mentve: {path}")

    def save_pdf(self):
        path = os.path.join(self.get_output_folder(), "prashna_elemzes.pdf")
        printer = QPrinter()
        printer.setOutputFileName(path)
        printer.setOutputFormat(QPrinter.PdfFormat)
        doc = QTextDocument(self.resultArea.toPlainText())
        doc.print_(printer)
        self.resultArea.append(f"📄 PDF mentve: {path}")

    def read_text(self):
        engine = pyttsx3.init()
        engine.say(self.resultArea.toPlainText())
        engine.runAndWait()

import os
import pendulum
import swisseph as swe
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QTimeEdit,
    QPushButton, QTextEdit, QComboBox
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument, QPixmap
from PyQt5.QtWidgets import QLabel
import pyttsx3

from modulok import astro_core, harmonizacio, audio_kotta_tools, draw
from modulok.tables import varga_factors

class RasiWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Személy 1
        self.name1 = QLineEdit()
        self.date1 = QDateEdit()
        self.time1 = QTimeEdit()
        self.lon1 = QLineEdit()
        self.lat1 = QLineEdit()
        self.place1 = QLineEdit()

        # Személy 2
        self.name2 = QLineEdit()
        self.date2 = QDateEdit()
        self.time2 = QTimeEdit()
        self.lon2 = QLineEdit()
        self.lat2 = QLineEdit()
        self.place2 = QLineEdit()

        # Időzóna és varga
        self.timezoneSelector = QComboBox()
        self.timezoneSelector.addItems([
            "Europe/Budapest", "UTC", "Asia/Kolkata", "America/New_York", "Australia/Sydney"
        ])
        self.vargaSelector = QComboBox()
        self.vargaSelector.addItems(list(varga_factors.keys()))

        # Gombok
        self.calc1 = QPushButton("Számol – 1. személy")
        self.calc2 = QPushButton("Számol – 2. személy")
        self.harmonizeButton = QPushButton("Harmonizáció")
        self.musicButton = QPushButton("Megzenésítés")
        self.savePDF = QPushButton("Mentés PDF-be")
        self.readAloud = QPushButton("Felolvasás")

        # Eredmény és kép
        self.resultArea = QTextEdit()
        self.chartImage = QLabel()

        # Layout
        for label, widget in [
            ("Név 1", self.name1), ("Dátum 1", self.date1), ("Idő 1", self.time1),
            ("Hely 1", self.place1), ("Szélesség 1", self.lat1), ("Hosszúság 1", self.lon1),
            ("Név 2", self.name2), ("Dátum 2", self.date2), ("Idő 2", self.time2),
            ("Hely 2", self.place2), ("Szélesség 2", self.lat2), ("Hosszúság 2", self.lon2),
            ("Időzóna", self.timezoneSelector), ("Varga chart", self.vargaSelector)
        ]:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        for btn in [self.calc1, self.calc2, self.harmonizeButton, self.musicButton, self.savePDF, self.readAloud]:
            layout.addWidget(btn)

        layout.addWidget(self.resultArea)
        layout.addWidget(self.chartImage)
        self.setLayout(layout)

        # Gombok összekötése
        self.calc1.clicked.connect(self.calculate_chart1)
        self.calc2.clicked.connect(self.calculate_chart2)
        self.harmonizeButton.clicked.connect(self.harmonize)
        self.musicButton.clicked.connect(self.musicalize)
        self.savePDF.clicked.connect(self.save_pdf)
        self.readAloud.clicked.connect(self.read_text)

    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "SonicJyotish")
        os.makedirs(folder, exist_ok=True)
        return folder

    def get_jd(self, date, time, tz):
        dt = pendulum.parse(f"{date}T{time}", tz=tz).in_timezone("UTC")
        return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60)

    def calculate_chart1(self):
        name = self.name1.text()
        date = self.date1.date().toString("yyyy-MM-dd")
        time = self.time1.time().toString("HH:mm")
        tz = self.timezoneSelector.currentText()
        lat = float(self.lat1.text())
        lon = float(self.lon1.text())
        varga = self.vargaSelector.currentText()
        factor = varga_factors.get(varga, 1)

        jd = self.get_jd(date, time, tz)
        positions = astro_core.get_planet_data(jd, lat, lon)
        varga_pos = astro_core.calculate_varga_positions(positions, factor)

        draw.rajzol_del_indiai_horoszkop(
            varga_pos, tithi=1, horoszkop_nev=varga,
            date_str=date, time_str=time,
            vezeteknev="user", keresztnev=name
        )

        path = os.path.join(self.get_output_folder(), f"user_{name.lower()}_horoszkop_{varga.replace(' ', '_')}.png")
        self.chartImage.setPixmap(QPixmap(path))
        self.resultArea.setText(f"{varga} horoszkóp mentve:\n{path}")

    def calculate_chart2(self):
        self.resultArea.append("📌 2. személy horoszkóp számítása kész – harmonizációhoz használható.")

    def harmonize(self):
        bd1 = {"name": self.name1.text(), "lat": float(self.lat1.text()), "lon": float(self.lon1.text())}
        bd2 = {"name": self.name2.text(), "lat": float(self.lat2.text()), "lon": float(self.lon2.text())}
        mix, sr = harmonizacio.harmonize_two_people(bd1, bd2)
        path = os.path.join(self.get_output_folder(), "harmonizacio_duett.wav")
        audio_kotta_tools.write(path, sr, mix)
        self.resultArea.append(f"🎶 Harmonizáció mentve: {path}")

    def musicalize(self):
        birth_data = {
            "name": self.name1.text(),
            "date": self.date1.date().toString(),
            "time": self.time1.time().toString(),
            "lon": self.lon1.text(),
            "lat": self.lat1.text(),
            "place": self.place1.text()
        }
        mix, sr = harmonizacio.compute_person_mix(birth_data)
        path = os.path.join(self.get_output_folder(), "horoszkop_zene.wav")
        audio_kotta_tools.write(path, sr, mix)
        self.resultArea.append(f"🎵 Megzenésítés mentve: {path}")

    def save_pdf(self):
        path = os.path.join(self.get_output_folder(), "elemzes.pdf")
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
    def get_birth_data(self):
        return {
            "name": self.name1.text(),
            "date": self.date1.date().toString("yyyy-MM-dd"),
            "time": self.time1.time().toString("HH:mm"),
            "lat": self.lat1.text(),
            "lon": self.lon1.text(),
            "place": self.place1.text(),
            "timezone": self.timezoneSelector.currentText()
        }
    def get_planet_positions(self):
        date = self.date1.date().toString("yyyy-MM-dd")
        time = self.time1.time().toString("HH:mm")
        tz = self.timezoneSelector.currentText()
        dt = pendulum.parse(f"{date}T{time}", tz=tz).in_timezone("UTC")
        jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60)
        lat = float(self.lat1.text())
        lon = float(self.lon1.text())
        return astro_core.get_planet_data(jd, lat, lon)

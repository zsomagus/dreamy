
import os
import pendulum
import swisseph as swe
import pyttsx3
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QDateEdit, QTimeEdit,
    QComboBox, QPushButton, QTextEdit
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QTextDocument, QPixmap
from PyQt5.QtWidgets import QLabel

from modulok import astro_core, audio_kotta_tools, draw, varshaphala_tools

class VarshaphalaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Születési adatok
        self.name = QLineEdit()
        self.date = QDateEdit()
        self.time = QTimeEdit()
        self.lat = QLineEdit()
        self.lon = QLineEdit()
        self.place = QLineEdit()
        self.timezoneSelector = QComboBox()
        self.timezoneSelector.addItems([
            "Europe/Budapest", "UTC", "Asia/Kolkata", "America/New_York", "Australia/Sydney"
        ])

        # Évszám (életkor)
        self.ageInput = QLineEdit()

        # Gombok
        self.calcButton = QPushButton("Számolás")
        self.musicButton = QPushButton("Megzenésítés")
        self.savePDF = QPushButton("Mentés PDF-be")
        self.readAloud = QPushButton("Felolvasás")

        # Eredmény és kép
        self.resultArea = QTextEdit()
        self.chartImage = QLabel()

        # Layout
        for label, widget in [
            ("Név", self.name), ("Születési dátum", self.date), ("Születési idő", self.time),
            ("Hely", self.place), ("Szélesség", self.lat), ("Hosszúság", self.lon),
            ("Időzóna", self.timezoneSelector), ("Életkor", self.ageInput)
        ]:
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        for btn in [self.calcButton, self.musicButton, self.savePDF, self.readAloud]:
            layout.addWidget(btn)

        layout.addWidget(self.resultArea)
        layout.addWidget(self.chartImage)
        self.setLayout(layout)

        # Gombok összekötése
        self.calcButton.clicked.connect(self.calculate_varshaphala)
        self.musicButton.clicked.connect(self.musicalize)
        self.savePDF.clicked.connect(self.save_pdf)
        self.readAloud.clicked.connect(self.read_text)

    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "SonicJyotish")
        os.makedirs(folder, exist_ok=True)
        return folder

    def calculate_varshaphala(self):
        name = self.name.text()
        date_str = self.date.date().toString("yyyy-MM-dd")
        time_str = self.time.time().toString("HH:mm")
        tz = self.timezoneSelector.currentText()
        lat = float(self.lat.text())
        lon = float(self.lon.text())
        age = int(self.ageInput.text())

        szul_dt = pendulum.parse(f"{date_str}T{time_str}", tz=tz)
        szul_utc = szul_dt.in_timezone("UTC")

        jd, dt = varshaphala_tools.calculate_solar_return_jd(
            date_str, time_str, lat, lon, tz, szul_utc, age
        )

        chart_data = astro_core.get_planet_data(jd, lat, lon)
        draw.rajzol_del_indiai_horoszkop(
            chart_data,
            tithi=1,
            horoszkop_nev=f"Varshaphala_{age}",
            date_str=dt.to_date_string(),
            time_str=dt.to_time_string(),
            vezeteknev="user",
            keresztnev=name
        )

        path = os.path.join(self.get_output_folder(), f"user_{name.lower()}_varshaphala_{age}.png")
        self.chartImage.setPixmap(QPixmap(path))
        self.resultArea.setText(f"🌞 {age}. éves Varshaphala kiszámítva:\n{dt.to_datetime_string()}\nKép mentve: {path}")

    def musicalize(self):
        text = self.resultArea.toPlainText()
        mix, sr = audio_kotta_tools.text_to_music(text)
        path = os.path.join(self.get_output_folder(), "varshaphala_zene.wav")
        audio_kotta_tools.write(path, sr, mix)
        self.resultArea.append(f"🎵 Zene mentve: {path}")

    def save_pdf(self):
        path = os.path.join(self.get_output_folder(), "varshaphala_elemzes.pdf")
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

def calculate_varshaphala(self):
    name = self.birth_data["name"]
    date_str = self.birth_data["date"]
    time_str = self.birth_data["time"]
    tz = self.birth_data["timezone"]
    lat = float(self.birth_data["lat"])
    lon = float(self.birth_data["lon"])
    age = int(self.ageInput.text())

    szul_dt = pendulum.parse(f"{date_str}T{time_str}", tz=tz)
    szul_utc = szul_dt.in_timezone("UTC")

    jd, dt = varshaphala_tools.calculate_solar_return_jd(
        date_str, time_str, lat, lon, tz, szul_utc, age
    )

    chart_data = astro_core.get_planet_data(jd, lat, lon)
    draw.rajzol_del_indiai_horoszkop(
        chart_data,
        tithi=1,
        horoszkop_nev=f"Varshaphala_{age}",
        date_str=dt.to_date_string(),
        time_str=dt.to_time_string(),
        vezeteknev="user",
        keresztnev=name
    )

    path = os.path.join(self.get_output_folder(), f"user_{name.lower()}_varshaphala_{age}.png")
    self.chartImage.setPixmap(QPixmap(path))
    self.resultArea.setText(f"🌞 {age}. éves Varshaphala kiszámítva:\n{dt.to_datetime_string()}\nKép mentve: {path}")
def open_varshaphala(self):
    birth_data = {
        "name": self.name1.text(),
        "date": self.date1.date().toString("yyyy-MM-dd"),
        "time": self.time1.time().toString("HH:mm"),
        "lat": self.lat1.text(),
        "lon": self.lon1.text(),
        "place": self.place1.text(),
        "timezone": self.timezoneSelector.currentText()
    }
    self.varsha_window = VarshaphalaWidget(birth_data)
    self.varsha_window.show()
    self.varshaButton = QPushButton("Varshaphala – Éves horoszkóp")
    layout.addWidget(self.varshaButton)
    self.varshaButton.clicked.connect(self.open_varshaphala)

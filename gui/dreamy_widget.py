import os
import json
import pendulum
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QSizePolicy,
    QSplitter, QHBoxLayout, QTabWidget
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

from modulok.config import fill_coordinate_entries
from modulok.load_alomszotar import load_alomszotar
from modulok.prashna_engine import generate_prashna_pixmap
from modulok.music_prompt import build_music_prompt
from modulok.score_renderer import export_score_to_pdf_and_png
from modulok import sonic_dreamy
from gui.kotta_tab import createScoreTab, generate_score
from modulok.tables import tithi_info
from modulok import prashna_core
from modulok.prashna_engine import generate_prashna_pixmap


class DreammyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dream_log = []
        self.last_generated_audio_path = None
        self.player = QMediaPlayer()

        filepath = os.path.join(os.path.dirname(__file__), "..", "alomszotar.json")
        self.szotar = load_alomszotar(filepath)

        self.initUI()
        self.load_dreams()
        self.showMaximized()
      
    def initUI(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # --- Bal oldal ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.dreamText = QTextEdit()
        self.dreamText.setMaximumHeight(120)
        self.dreamText.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.dreamText.setPlaceholderText("Mit álmodtál?")

        self.moodSelector = QComboBox()
        self.moodSelector.addItems([
            "Nyugodt", "Zaklatott", "Misztikus",
            "Félelmetes", "Boldog", "Zavaros"
        ])

        self.keywordInput = QLineEdit()
        self.keywordInput.setPlaceholderText("Kulcsszavak (vesszővel elválasztva)")

        self.saveButton = QPushButton("✨ Mentés és értelmezés")

        self.resultArea = QTextEdit()
        self.resultArea.setReadOnly(True)

        # Táblázat
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Dátum", "Hangulat", "Kulcsszavak", "Szimbolumok", "Leírás"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Tabok
        self.tabs = QTabWidget()
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        table_layout.addWidget(self.table)
        self.tabs.addTab(table_tab, "Napló")

        left_layout.addWidget(QLabel("📝 Új álom"))
        left_layout.addWidget(self.dreamText)
        left_layout.addWidget(QLabel("Hangulat"))
        left_layout.addWidget(self.moodSelector)
        left_layout.addWidget(QLabel("Kulcsszavak"))
        left_layout.addWidget(self.keywordInput)
        left_layout.addWidget(self.saveButton)
        left_layout.addWidget(QLabel("🔮 Értelmezés"))
        left_layout.addWidget(self.resultArea)
        left_layout.addWidget(QLabel("📜 Korábbi álmok"))
        left_layout.addWidget(self.tabs)

        # --- Jobb oldal ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        title_label = QLabel("🕉️ Prashna horoszkóp (yantrával), segíti az álomfejtést.")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #008080;")
        right_layout.addWidget(title_label)

        self.prashnaLabel = QLabel()
        self.prashnaLabel.setMinimumSize(400, 400)
        self.prashnaLabel.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.prashnaLabel)

        self.coordButton = QPushButton("📍 Prashna koordináták / hely")
        right_layout.addWidget(self.coordButton)

        
    # ---------- Kimeneti mappa ----------
    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "Álmaim")
        os.makedirs(folder, exist_ok=True)
        return folder

    # ---------- Ragozás ----------
    def levag_ragokat(self, szo: str) -> str:
        ragok = ["ban", "ben", "val", "vel", "hoz", "hez", "höz",
                 "nak", "nek", "t", "k", "ok", "ek", "ök"]
        for rag in ragok:
            if szo.lower().endswith(rag):
                return szo[:-len(rag)]
        return szo

    # ---------- Mentés + értelmezés ----------
    def save_and_analyze(self):
        text = self.dreamText.toPlainText().strip()
        if not text:
            return

        mood = self.moodSelector.currentText().strip()
        keywords = self.keywordInput.text().strip()
        now = pendulum.now("Europe/Budapest")
        date_only = now.format("YYYY-MM-DD")
        datum_str = now.format("YYYY-MM-DD HH:mm")

        # Álomszótár
        talalatok = []
        szimbolumok = []

        szavak = text.split()
        szavak_tovei = [self.levag_ragokat(szo) for szo in szavak]

        for kulcs in self.szotar.keys():
            for szo in szavak_tovei:
                if kulcs.lower() == szo.lower():
                    szimbolumok.append(kulcs)
                    talalatok.append(f"{kulcs}: {self.szotar[kulcs]}")

        entry = {
            "Dátum": datum_str,
            "Hangulat": mood,
            "Kulcsszavak": keywords,
            "Leírás": text,
            "Szimbolumok": szimbolumok,
        }
        self.dream_log.append(entry)
        self.save_to_file()
        self.update_table()

        if talalatok:
            self.resultArea.setText("🔮 Értelmezések:\n" + "\n".join(talalatok))
        else:
            self.resultArea.setText("Nincs találat az álomszótárban.")

        # Prashna horoszkóp
        self.generate_prashna_chart()

        # Sonic Jyotish hang generálás
        try:
            output_path = sonic_dreamy.generate_full_audio(
                "User", 1990, 1, 1, 12, 0, "Europe/Budapest", 19.04, 47.49
            )
            self.last_generated_audio_path = output_path


    # ---------- JSON ----------
    def save_to_file(self):
        path = os.path.join(self.get_output_folder(), "dream_log.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.dream_log, f, ensure_ascii=False, indent=2)

    def load_dreams(self):
        path = os.path.join(self.get_output_folder(), "dream_log.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.dream_log = json.load(f)
            self.update_table()

    # ---------- Táblázat ----------
    def update_table(self):
        self.table.setRowCount(0)
        for dream in reversed(self.dream_log):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(dream.get("Dátum", "")))
            self.table.setItem(row, 1, QTableWidgetItem(dream.get("Hangulat", "")))
            self.table.setItem(row, 2, QTableWidgetItem(dream.get("Kulcsszavak", "")))
            self.table.setItem(row, 3, QTableWidgetItem(", ".join(dream.get("Szimbolumok", []))))
            self.table.setItem(row, 4, QTableWidgetItem(dream.get("Leírás", "")))

    # ---------- Prashna ----------
    
    def generate_prashna_chart(self):
        lat = getattr(self, "prashna_latitude", 46.857222)
        lon = getattr(self, "prashna_longitude", 18.15333)

        prashna = prashna_core.fill_prashna_data_with_coords(lat, lon)
        tithi = prashna.get("tithi")

        pixmap = generate_prashna_pixmap(lat, lon)
        self.current_prashna_pixmap = pixmap
        self.update_prashna_pixmap()

        info = tithi_info.get(tithi, {})
        nev = info.get("nev", f"Tithi {tithi}")
        jelentes = info.get("jelentes", "–")
        ajanlas = info.get("ajanlas", "")

        if not ajanlas:
            ajanlas = "🌑 Csendes nap – figyelj befelé"

        self.tithiLabel.setText(
            f"<b>{nev}</b><br>"
            f"{jelentes}<br>"
            f"<i>{ajanlas}</i>"
        )


    def update_prashna_pixmap(self):
        if not hasattr(self, "current_prashna_pixmap"):
            return

        scaled = self.current_prashna_pixmap.scaled(
            self.prashnaLabel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.prashnaLabel.setPixmap(scaled)

    # ---------- Koordináta panel ----------
    def show_coord_panel(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Prashna koordináták / hely")

        layout = QFormLayout(dialog)

        city_input = QLineEdit()
        lat_input = QLineEdit(str(getattr(self, "prashna_latitude", 46.857222)))
        lon_input = QLineEdit(str(getattr(self, "prashna_longitude", 18.153333)))

        layout.addRow("Hely (város):", city_input)
        layout.addRow("Szélesség:", lat_input)
        layout.addRow("Hosszúság:", lon_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(buttons)

        def keres():
            city = city_input.text().strip()
            if city:
                found = fill_coordinate_entries(city, lat_input, lon_input)
                if not found:
                    lat_input.setPlaceholderText("Nem található, kézzel is beírható")
                    lon_input.setPlaceholderText("Nem található, kézzel is beírható")

        city_input.editingFinished.connect(keres)

        def accept():
            try:
                lat = float(lat_input.text())
                lon = float(lon_input.text())
                self.prashna_latitude = lat
                self.prashna_longitude = lon
            except ValueError:
                pass
            dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec_()

    # ---------- Resize ----------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_prashna_pixmap()

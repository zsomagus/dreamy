import os
import json
import pendulum

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QSizePolicy
from PyQt5.QtWidgets import QSplitter, QHBoxLayout

from modulok.config import fill_coordinate_entries

from modulok.load_alomszotar import load_alomszotar
from modulok import prashna_core
from modulok.draw import rajzol_del_indiai_horoszkop


class DreammyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dream_log = []

        filepath = os.path.join(os.path.dirname(__file__), "..", "alomszotar.json")
        self.szotar = load_alomszotar(filepath)

        self.initUI()
        self.load_dreams()
        self.showMaximized()


    def initUI(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

    # --- Bal oldal: álomnapló + táblázat ---
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

        self.saveButton = QPushButton("✨ Mentés és értelmezés")
        self.resultArea = QTextEdit()
        self.resultArea.setReadOnly(True)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Dátum", "Álom", "Hangulat", "Szimbolumok"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        left_layout.addWidget(QLabel("📝 Új álom"))
        left_layout.addWidget(self.dreamText)
        left_layout.addWidget(QLabel("Hangulat"))
        left_layout.addWidget(self.moodSelector)
        left_layout.addWidget(self.saveButton)
        left_layout.addWidget(QLabel("🔮 Értelmezés"))
        left_layout.addWidget(self.resultArea)
        left_layout.addWidget(QLabel("📜 Korábbi álmok"))
        left_layout.addWidget(self.table)

    # --- Jobb oldal: horoszkóp + koordináta gomb ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        title_label = QLabel("🕉️ Prashna horoszkóp (yantrával), segíti az álomfejtést.")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #008080;")
        right_layout.addWidget(title_label)

        self.prashnaLabel = QLabel()
        self.prashnaLabel.setScaledContents(False)
        self.prashnaLabel.setMinimumSize(400, 400)
        self.prashnaLabel.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.prashnaLabel, alignment=Qt.AlignCenter)

        self.coordButton = QPushButton("📍 Prashna koordináták / hely")
        right_layout.addWidget(self.coordButton)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 700])

        self.saveButton.clicked.connect(self.save_and_analyze)
        self.coordButton.clicked.connect(self.show_coord_panel)


    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "Álmaim")
        os.makedirs(folder, exist_ok=True)
        return folder

    def levag_ragokat(self, szo: str) -> str:
        ragok = [
            "ban", "ben", "val", "vel", "hoz", "hez", "höz",
            "nak", "nek", "t", "k", "ok", "ek", "ök",
        ]
        for rag in ragok:
            if szo.lower().endswith(rag):
                return szo[:-len(rag)]
        return szo

    def save_and_analyze(self):
        text = self.dreamText.toPlainText().strip()
        if not text:
            return

        mood = self.moodSelector.currentText()
        now = pendulum.now("Europe/Budapest")
        datum_str = now.format("YYYY-MM-DD HH:mm")

        # Álomszótár értelmezés
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
            "Álom": text,
            "Hangulat": mood,
            "Szimbolumok": ", ".join(szimbolumok),
        }
        self.dream_log.append(entry)
        self.save_to_file()
        self.update_table()

        if talalatok:
            self.resultArea.setText("🔮 Értelmezések:\n" + "\n".join(talalatok))
        else:
            self.resultArea.setText("Nincs találat az álomszótárban.")

        # Prashna horoszkóp generálása
        self.generate_prashna_chart()

        self.dreamText.clear()

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

    def update_table(self):
        self.table.setRowCount(len(self.dream_log))
        for i, dream in enumerate(reversed(self.dream_log)):
            self.table.setItem(i, 0, QTableWidgetItem(dream.get("Dátum", "")))
            self.table.setItem(i, 1, QTableWidgetItem(dream.get("Álom", "")))
            self.table.setItem(i, 2, QTableWidgetItem(dream.get("Hangulat", "")))
            szimb = dream.get("Szimbolumok") or dream.get("Kulcsszo") or ""
            self.table.setItem(i, 3, QTableWidgetItem(szimb))

    def generate_prashna_chart(self):
        latitude = getattr(self, "prashna_latitude", 46.857222)
        longitude = getattr(self, "prashna_longitude", 18.15333)

        prashna = prashna_core.fill_prashna_data_with_coords(latitude, longitude)
        planet_data = prashna["chart_data"]

        moon_lon = planet_data["Moon"]["longitude"]
        sun_lon = planet_data["Sun"]["longitude"]
        tithi = int(((moon_lon - sun_lon) % 360) / 12) + 1

        pixmap = rajzol_del_indiai_horoszkop(
            planet_data,
            tithi,
            horoszkop_nev="D1",
            date_str=prashna["date"],
            time_str=prashna["time"],
            is_prashna=True,
        )

        self.current_prashna_pixmap = pixmap
        self.update_prashna_pixmap()

    def update_prashna_pixmap(self):
        if not hasattr(self, "current_prashna_pixmap"):
            return

        scaled = self.current_prashna_pixmap.scaled(
            self.prashnaLabel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.prashnaLabel.setPixmap(scaled)

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_prashna_pixmap()

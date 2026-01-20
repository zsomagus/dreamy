import os
import json
import pendulum

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

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

    def initUI(self):
        layout = QVBoxLayout()

        # Új álom bejegyzés
        self.dreamText = QTextEdit()
        self.dreamText.setPlaceholderText("Mit álmodtál?")

        self.moodSelector = QComboBox()
        self.moodSelector.addItems([
            "Nyugodt", "Zaklatott", "Misztikus",
            "Félelmetes", "Boldog", "Zavaros"
        ])

        self.saveButton = QPushButton("✨ Mentés és értelmezés")
        self.resultArea = QTextEdit()
        self.resultArea.setReadOnly(True)

        # Táblázat
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Dátum", "Álom", "Hangulat", "Szimbolumok"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(QLabel("📝 Új álom"))
        layout.addWidget(self.dreamText)
        layout.addWidget(QLabel("Hangulat"))
        layout.addWidget(self.moodSelector)
        layout.addWidget(self.saveButton)
        layout.addWidget(QLabel("🔮 Értelmezés"))
        layout.addWidget(self.resultArea)
        layout.addWidget(QLabel("📜 Korábbi álmok"))
        layout.addWidget(self.table)

        # Prashna horoszkóp (yantrával a közepén)
        self.prashnaLabel = QLabel()
        self.prashnaLabel.setScaledContents(False)
        self.prashnaLabel.setMinimumHeight(300)

        layout.addWidget(QLabel("🕉️ Prashna horoszkóp (yantrával)"))
        layout.addWidget(self.prashnaLabel)

        self.setLayout(layout)
        self.saveButton.clicked.connect(self.save_and_analyze)

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
        prashna = prashna_core.fill_prashna_data()
        planet_data = prashna["chart_data"]

        moon_lon = planet_data["Moon"]["longitude"]
        sun_lon = planet_data["Sun"]["longitude"]
        tithi = int(((moon_lon - sun_lon) % 360) / 12) + 1

        rajzol_del_indiai_horoszkop(
            planet_data,
            tithi,
            horoszkop_nev="D1",
            date_str=prashna["date"],
            time_str=prashna["time"],
            vezeteknev=None,
            keresztnev=None,
            is_prashna=True,
        )

        downloads = os.path.join(os.path.expanduser("~"), "Downloads", "SonicJyotish")
        datum = prashna["date"].strip()
        ido = prashna["time"].strip().replace(":", "-")
        filename = os.path.join(downloads, f"prashna_{datum}_{ido}_D1.png")

        if os.path.exists(filename):
            self.current_prashna_path = filename
            self.update_prashna_pixmap()
        else:
            self.prashnaLabel.setText("A prashna horoszkóp képe nem található.")

    def update_prashna_pixmap(self):
        if not hasattr(self, "current_prashna_path"):
            return

        pix = QPixmap(self.current_prashna_path)
        if pix.isNull():
            return

        scaled = pix.scaled(
            self.prashnaLabel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.prashnaLabel.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_prashna_pixmap()

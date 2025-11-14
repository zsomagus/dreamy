import os, json
import pendulum
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox,
    QListWidget, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from modulok import prashna_core, astro_core, dasa_tools

class DreammyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dream_log = []
        self.initUI()
        self.load_dreams()

    def initUI(self):
        layout = QVBoxLayout()

        self.dreamText = QTextEdit()
        self.dreamText.setPlaceholderText("Mit álmodtál?")
        self.moodSelector = QComboBox()
        self.moodSelector.addItems(["Nyugodt", "Zaklatott", "Misztikus", "Félelmetes", "Boldog", "Zavaros"])
        self.symbolSelector = QListWidget()
        self.symbolSelector.addItems(["Víz", "Kígyó", "Tükör", "Repülés", "Tűz", "Hold", "Ismeretlen személy"])
        self.symbolSelector.setSelectionMode(QListWidget.MultiSelection)

        self.saveButton = QPushButton("✨ Mentés")
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Dátum", "Álom", "Hangulat", "Szimbólumok", "Daśa-trió"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(QLabel("📝 Új álom bejegyzése"))
        layout.addWidget(self.dreamText)
        layout.addWidget(QLabel("Hangulat"))
        layout.addWidget(self.moodSelector)
        layout.addWidget(QLabel("Szimbólumok"))
        layout.addWidget(self.symbolSelector)
        layout.addWidget(self.saveButton)
        layout.addWidget(QLabel("📜 Korábbi álmok"))
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.saveButton.clicked.connect(self.save_dream)

    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "SonicJyotish")
        os.makedirs(folder, exist_ok=True)
        return folder

    def get_dasa_trio_for_dream(self, chart_data, dream_dt_str):
        dt = pendulum.parse(dream_dt_str, tz="Europe/Budapest")
        jd = astro_core.swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60)
        positions = astro_core.get_planet_data(jd, 47.4979, 19.0402)
        dasa_info = dasa_tools.calculate_dasa_info(positions)
        return f"{dasa_info['Mahadasa']['planet']} / {dasa_info['Antardasa']['planet']} / {dasa_info['Pratyantardasa']['planet']}"

    def save_dream(self):
        text = self.dreamText.toPlainText().strip()
        if not text:
            return

        mood = self.moodSelector.currentText()
        symbols = [item.text() for item in self.symbolSelector.selectedItems()]
        now = pendulum.now("Europe/Budapest")
        datum_str = now.format("YYYY-MM-DD HH:mm")

        jd = astro_core.swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60)
        chart_data = astro_core.get_planet_data(jd, 47.4979, 19.0402)
        dasa_trio = self.get_dasa_trio_for_dream(chart_data, datum_str)

        entry = {
            "Dátum": datum_str,
            "Álom": text,
            "Hangulat": mood,
            "Szimbólumok": ", ".join(symbols),
            "Daśa-trió": dasa_trio
        }

        self.dream_log.append(entry)
        self.save_to_file()
        self.update_table()

        self.dreamText.clear()
        self.symbolSelector.clearSelection()

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
            self.table.setItem(i, 0, QTableWidgetItem(dream["Dátum"]))
            self.table.setItem(i, 1, QTableWidgetItem(dream["Álom"]))
            self.table.setItem(i, 2, QTableWidgetItem(dream["Hangulat"]))
            self.table.setItem(i, 3, QTableWidgetItem(dream["Szimbólumok"]))
            self.table.setItem(i, 4, QTableWidgetItem(dream["Daśa-trió"]))

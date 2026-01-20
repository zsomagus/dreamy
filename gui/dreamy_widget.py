import os, json, pendulum
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox,
    QListWidget, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from modulok.load_alomszotar import load_alomszotar, keres_alomjelentes
from modulok import astro_core, draw, prashna_core
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
        self.moodSelector.addItems(["Nyugodt","Zaklatott","Misztikus","Félelmetes","Boldog","Zavaros"])
        self.saveButton = QPushButton("✨ Mentés és értelmezés")
        self.resultArea = QTextEdit()

        # Táblázat
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Dátum","Álom","Hangulat", "Szimbolumok"])
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

        self.setLayout(layout)
        self.saveButton.clicked.connect(self.save_and_analyze)

    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "Álmaim")
        os.makedirs(folder, exist_ok=True)
        return folder

    def save_and_analyze(self):
        text = self.dreamText.toPlainText().strip()
        if not text:
            return
        mood = self.moodSelector.currentText()
        now = pendulum.now("Europe/Budapest")
        datum_str = now.format("YYYY-MM-DD HH:mm")

    # 🔮 Álomszótár értelmezés + kulcsszavak gyűjtése
        talalatok = []
        szimbolumok = []
        
        # Szavakra bontás
        szavak = text.split()
    # Levágjuk a ragokat
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
            self.table.setItem(i, 0, QTableWidgetItem(dream["Dátum"]))
            self.table.setItem(i, 1, QTableWidgetItem(dream["Álom"]))
            self.table.setItem(i, 2, QTableWidgetItem(dream["Hangulat"]))
            # kompatibilis régi és új kulcsnévvel
            szimb = dream.get("Szimbolumok") or dream.get("Kulcsszo") or ""
            self.table.setItem(i, 3, QTableWidgetItem(szimb))
    def levag_ragokat(self, szo: str):
        """Levágja a leggyakoribb magyar ragokat a szó végéről."""
        ragok = [
            "ban","ben","val","vel","hoz","hez","höz",
            "nak","nek","t","k","ok","ek","ök","ban","ben",
            "ban","ben","ban","ben"  # duplázás elkerülhető
        ]
        for rag in ragok:
            if szo.lower().endswith(rag):
                return szo[:-len(rag)]
        return szo

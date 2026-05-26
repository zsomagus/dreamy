import os
import json
import pendulum

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QSizePolicy,
    QSplitter, QHBoxLayout, QTabWidget
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from modulok import astro_core
from modulok.draw import rajzol_del_indiai_horoszkop
from modulok.config import fill_coordinate_entries
from modulok.load_alomszotar import load_alomszotar
from modulok.tables import tithi_info
from modulok import prashna_core
# Importáljuk a zenei prompt készítőt
from modulok.music_prompt import build_music_prompt
from modulok.score_renderer import export_score_to_pdf_and_png  # <-- Ezt adjuk hozzá!
class DreammyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dream_log = []
        self.current_prashna_pixmap = None

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

        # Táblázat és fül rendszer
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Dátum", "Hangulat", "Kulcsszavak", "Szimbolumok", "Leírás"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.tabs = QTabWidget()
        
        # 1. Tab: Napló táblázat
        table_tab = QWidget()
        table_layout = QVBoxLayout(table_tab)
        table_layout.addWidget(self.table)
        self.tabs.addTab(table_tab, "Napló")

        # 2. Tab: AI Prompt fül (Kimásolható szövegmezővel)
        self.score_tab = QWidget()
        score_layout = QVBoxLayout(self.score_tab)
        
        prompt_label = QLabel("📋 Generált AI Prompt (Kimásolható zene és kép készítéséhez):")
        prompt_label.setStyleSheet("font-weight: bold; color: #4b5263;")
        score_layout.addWidget(prompt_label)

        self.scoreInfo = QTextEdit()
        self.scoreInfo.setReadOnly(True)  # Csak olvasható, de kijelölhető és másolható
        self.scoreInfo.setStyleSheet("font-family: Consolas, Monaco, monospace; background-color: #f8f9fa;")
        score_layout.addWidget(self.scoreInfo)

        self.tabs.addTab(self.score_tab, "🎵 AI Prompt Szöveg")

        left_layout.addWidget(QLabel("📝 Új álom"))
        left_layout.addWidget(self.dreamText)
        left_layout.addWidget(QLabel("Hangulat"))
        left_layout.addWidget(self.moodSelector)
        left_layout.addWidget(QLabel("Kulcsszavak"))
        left_layout.addWidget(self.keywordInput)
        left_layout.addWidget(self.saveButton)
        left_layout.addWidget(QLabel("🔮 Értelmezés-Egy kis segítség az álomfejtésben"))
        left_layout.addWidget(self.resultArea)
        left_layout.addWidget(QLabel("📜 Előzmények"))
        left_layout.addWidget(self.tabs)

        # --- Jobb oldal ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        title_label = QLabel("🕉️ Prashna horoszkóp (yantrával)-Még egy kis segitség az álom megfejtéséhez.")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #008080;")
        right_layout.addWidget(title_label)

        self.prashnaLabel = QLabel()
        self.prashnaLabel.setMinimumSize(400, 400)
        self.prashnaLabel.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.prashnaLabel)

        self.tithiLabel = QLabel()
        self.tithiLabel.setStyleSheet("font-size: 14px; color: #333333;")
        self.tithiLabel.setWordWrap(True)
        right_layout.addWidget(self.tithiLabel)

        self.coordButton = QPushButton("📍 Prashna koordináták / hely")
        right_layout.addWidget(self.coordButton)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Eseménykezelők bekötése
        self.saveButton.clicked.connect(self.save_and_analyze)
        self.coordButton.clicked.connect(self.show_coord_panel)
        
    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "Álmaim")
        os.makedirs(folder, exist_ok=True)
        return folder

    def levag_ragokat(self, szo: str) -> str:
        ragok = ["ban", "ben", "val", "vel", "hoz", "hez", "höz",
                 "nak", "nek", "t", "k", "ok", "ek", "ök"]
        for rag in ragok:
            if szo.lower().endswith(rag):
                return szo[:-len(rag)]
        return szo

    # ---------- Mentés + értelmezés ----------
# A dreamy_widget.py megfelelő import szekciójába:

    def save_and_analyze(self):
        import pendulum
        import os  # 🎯 JAVÍTÁS: Nagyon fontos, különben a függvény vége NameError-t dob!
        
        text = self.dreamText.toPlainText().strip()
        if not text:
            return

        mood = self.moodSelector.currentText().strip()
        keywords = self.keywordInput.text().strip()
        now = pendulum.now("Europe/Budapest")
        datum_str = now.format("YYYY-MM-DD HH:mm")
        
        # 🕒 IDŐKÓD GENERÁLÁSA A FÁJLNEVEKHEZ (Pl: 20260523_160530)
        idokod = now.format("YYYYMMDD_HHmmss")

        # Álomszótár keresés
        talalatok = []
        szimbolumok = []
        szavak = text.split()
        szavak_tovei = [self.levag_ragokat(szo) for szo in szavak]

        for kulcs in self.szotar.keys():
            for szo in szavak_tovei:
                if kulcs.lower() == szo.lower():
                    szimbolumok.append(kulcs)
                    talalatok.append(f"{kulcs}: {self.szotar[kulcs]}")

        # JSON napló mentése
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

        # ─── PRASHNA HOROSZKÓP FRISSÍTÉS ───
        # ─── PRASHNA HOROSZKÓP FRISSÍTÉS ───
        pixmap = self.generate_prashna_chart()
        
        if pixmap:
            self.current_prashna_pixmap = pixmap
            # 🎯 JAVÍTÁS: Közvetlenül a felületen létező self.prashnaLabel-re tesszük rá a képet!
            self.update_prashna_pixmap()
            # Dinamikusan megkeressük azt a QLabel-t, ami a horoszkópé
            from PyQt5.QtWidgets import QLabel
            labels = self.findChildren(QLabel)
            for lbl in labels:
                # Olyan üres labeleket keresünk, amik nem a kottához tartoznak
                if not lbl.text() and lbl != getattr(self, 'score_chart_label', None):
                    lbl.setPixmap(pixmap)
                    lbl.setScaledContents(True)  # Szépen méretezi a sárga ábrát a cellában
                    break

        # ─── 🎵 KOTTA ÉS PROMPT GENERÁLÁSI LÁNC A FÜGGVÉNY VÉGÉN ───
        # 1. Összeállítjuk az angol AI szöveget
        prompt_text = build_music_prompt(text, mood, keywords, szimbolumok)
        
        # 2. Megjelenítjük a nyers, másolható szöveget a szövegdobozban
        self.scoreInfo.setText(prompt_text)

        # 3. Kotta PDF és PNG generálása és mentése IDŐKÓDDAL az Álmaim mappába
        folder = self.get_output_folder()  # Letöltések/Álmaim
        bázis_név = f"kotta_prompt_{idokod}"
        
        # Meghívjuk a kottalap készítőt
        pdf_ut, png_ut = export_score_to_pdf_and_png(prompt_text, folder, bázis_név)

        # 4. A legenerált kottalap képének azonnali betöltése a felületre!
        if os.path.exists(png_ut):
            self.current_score_pixmap = QPixmap(png_ut)
            self.update_score_pixmap()
    # ---------- Prashna ----------
    def generate_prashna_chart(self):
        # 🎯 JAVÍTÁS: A valós, koordináta panel által elmentett változókat olvassuk be!
        # Ha még nem nyitottad meg a panelt, alapértelmezetten Budapest (47.4979, 19.0402)
        lat = getattr(self, "prashna_latitude", 47.4979)
        lon = getattr(self, "prashna_longitude", 19.0402)

        import pendulum
        from modulok import astro_core
        from modulok.draw import rajzol_del_indiai_horoszkop

        now = pendulum.now("Europe/Budapest")

        # Hajszálpontos védikus adatok lekérése a megfelelő időzónával
        res = astro_core.get_varga_chart_data(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=now.hour,
            minute=now.minute,
            lat=lat,
            lon=lon,
            timezone_offset=now.utcoffset().total_seconds() / 3600,
            varga_label="D1 (Rashi)"
        )

        # Frissítjük a Tithi feliratot is a horoszkóp alatt, hogy látszódjon az eredmény
        if "tithi" in res:
            from modulok.tables import tithi_info
            t_num = res["tithi"]
            t_nev = tithi_info.get(t_num, {}).get("hu", "")
            t_leiras = tithi_info.get(t_num, {}).get("leiras", "")
            self.tithiLabel.setText(f"<b>Tithi: {t_num} - {t_nev}</b><br/>{t_leiras}")

        # Horoszkóp megrajzolása (A draw.py most már megkapja a valós, jó adatokat!)
        pixmap = rajzol_del_indiai_horoszkop(
            planet_data=res["planet_data"],
            tithi=res["tithi"],
            horoszkop_nev="D1",
            is_prashna=True
        )
        
        return pixmap
    def update_prashna_pixmap(self):
        if not self.current_prashna_pixmap:
            return
        scaled = self.current_prashna_pixmap.scaled(
            self.prashnaLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.prashnaLabel.setPixmap(scaled)
    def update_score_pixmap(self):
        """Ez a függvény felelős a zenei kottalap képének frissítéséért"""
        if not hasattr(self, 'current_score_pixmap') or not self.current_score_pixmap:
            return
        
        # Ugyanaz a skálázás, mint a prashnánál, csak a scoreInfo-hoz igazítva
        scaled = self.current_score_pixmap.scaled(
            self.scoreInfo.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        # Ha van egy külön QLabel-ed a kottának (pl. scorePreview), akkor arra rakjuk rá:
        if hasattr(self, 'scorePreview'):
            self.scorePreview.setPixmap(scaled)
    # ---------- Koordináta panel ----------
    def show_coord_panel(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Prashna koordináták")
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
           fill_coordinate_entries(city, lat_input, lon_input)

        city_input.editingFinished.connect(keres)

    def accept():
        try:
            self.prashna_latitude = float(lat_input.text())
            self.prashna_longitude = float(lon_input.text())
            self.generate_prashna_chart()
        except ValueError:
            pass
        dialog.accept()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(dialog.reject)
        dialog.exec_()

    # ---------- Fájl műveletek ----------
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
        self.table.setRowCount(0)
        for dream in reversed(self.dream_log):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(dream.get("Dátum", "")))
            self.table.setItem(row, 1, QTableWidgetItem(dream.get("Hangulat", "")))
            self.table.setItem(row, 2, QTableWidgetItem(dream.get("Kulcsszavak", "")))
            self.table.setItem(row, 3, QTableWidgetItem(", ".join(dream.get("Szimbolumok", []))))
            self.table.setItem(row, 4, QTableWidgetItem(dream.get("Leírás", "")))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_prashna_pixmap()
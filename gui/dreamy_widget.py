import os
import json
import pendulum
from datetime import datetime

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
from modulok.load_alomszotar import load_alomszotar, keres_alomjelentes
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
        self.current_prashna_pixmap = None
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
            "Félelmetes", "Boldog", "Zavaros,", "Relaxált/Meditatív"
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

        title_label = QLabel("🕉️ Prashna Elemzés")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #008080;")
        right_layout.addWidget(title_label)

        # Létrehozunk egy új fülke-kezelőt a jobb oldali asztrológiai résznek
        self.astro_tabs = QTabWidget()

        # ─── 1. FÜL: HOROSZKÓP ÁBRA ───
        chart_tab = QWidget()
        chart_tab_layout = QVBoxLayout(chart_tab)
        
        self.prashnaLabel = QLabel()
        self.prashnaLabel.setMinimumSize(400, 400)
        self.prashnaLabel.setAlignment(Qt.AlignCenter)
        chart_tab_layout.addWidget(self.prashnaLabel)
        
        self.astro_tabs.addTab(chart_tab, "📊 Prashna Horoszkóp")

        # ─── 2. FÜL: TITHI YANTRA ───
        yantra_tab = QWidget()
        yantra_tab_layout = QVBoxLayout(yantra_tab)
        
        self.yantra_label = QLabel("A Yantra az elemzés után itt fog megjelenni")
        self.yantra_label.setAlignment(Qt.AlignCenter)
        # Gyönyörű sárgás háttér, ami illik a horoszkóphoz
        self.yantra_label.setStyleSheet("background-color: #FFA500; border: 3px solid green; padding: 10px; font-weight: bold;")
        yantra_tab_layout.addWidget(self.yantra_label)
        
        self.astro_tabs.addTab(yantra_tab, "🔮 Tithi Yantra")

        # Hozzáadjuk a füleket a jobb oldali fő layout-hoz
        right_layout.addWidget(self.astro_tabs)
        
        # Tithi leírás és Koordináta gomb az ablak alján maradnak stabilan
        self.tithiLabel = QLabel()
        self.tithiLabel.setStyleSheet("font-size: 14px; color: #333333;")
        self.tithiLabel.setWordWrap(True)
        right_layout.addWidget(self.tithiLabel)

        self.coordButton = QPushButton("📍 Prashna koordináták / hely")
        right_layout.addWidget(self.coordButton)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

       # Eseménykezelők bekötése
        self.coordButton.clicked.connect(self.show_coord_panel)
        self.saveButton.clicked.connect(self.save_and_analyze)  # <-- EZ HIÁNYZOTT!
        
    def get_output_folder(self):
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        folder = os.path.join(downloads, "Álmaim")
        os.makedirs(folder, exist_ok=True)
        return folder
    def levag_ragokat(self, szo: str) -> str:
        # Szigorúbb, pontosabb rageltávolítás, hogy ne csonkítsa a szótöveket "he"-re és "ma"-ra
        ragok = ["ban", "ben", "val", "vel", "hoz", "hez", "höz",
                 "nak", "nek", "ból", "ből", "ről", "ről", "tól", "től"]
        for rag in ragok:
            if szo.lower().endswith(rag) and len(szo) > len(rag) + 2:
                return szo[:-len(rag)]
        
        # Külön kezeljük a tárgyragot és többes számot, de csak ha nem teszi tönkre a szót
        if len(szo) > 3:
            if szo.lower().endswith("t") and szo.lower()[-2] in ["a", "e", "o", "ó", "é"]:
                return szo[:-1]
            if szo.lower().endswith("k") and szo.lower()[-2] in ["o", "e", "ö", "a"]:
                return szo[:-2]
        return szo

    # ---------- Mentés + értelmezés ----------
    def save_and_analyze(self):
        import pendulum
        import os
        from PyQt5.QtGui import QPixmap
        from PyQt5.QtCore import Qt
        from modulok.music_prompt import build_music_prompt
        from modulok.score_renderer import export_score_to_pdf_and_png

        text = self.dreamText.toPlainText().strip()
        if not text:
            return

        mood = self.moodSelector.currentText().strip()
        keywords = self.keywordInput.text().strip()
        
        now = pendulum.now("Europe/Budapest")
        datum_str = now.format("YYYY-MM-DD HH:mm")
        idokod = now.format("YYYYMMDD_HHmmss")

        # === 🔮 ÁLOMSZÓTÁR MOTOR (HEGY HIBÁTÓL MEGTISZTÍTVA) ===
        talalatok = []
        szimbolumok = []
        
        szavak = [s.strip().lower() for s in text.split() if len(s.strip()) > 2]
        szavak_tovei = [self.levag_ragokat(s) for s in szavak]

        egyedi_kulcsszavak = [k.strip().lower() for k in keywords.split(",") if k.strip()]
        minden_keresett_kifejezes = list(set(szavak_tovei + egyedi_kulcsszavak))

        for szo in minden_keresett_kifejezes:
            if not szo or len(szo) < 3: # Túl rövid töredékeket (pl: "he", "ma") nem engedünk át
                continue
            for item in self.szotar.get("alomszotar", []):
                if isinstance(item, dict):
                    kulcsszo = item.get("kulcsszo", "").lower().strip()
                    
                    # Szigorú, értelmes egyezés: vagy pontosan egyezik, vagy a teljes szótári szó szerepel a beírt szövegben
                    if szo == kulcsszo or kulcsszo in szo:
                        jelentesek = item.get("jelentesek", [])
                        for j in jelentesek:
                            sor = f"• {kulcsszo.capitalize()}: {j}"
                            if sor not in talalatok:
                                talalatok.append(sor)
                        
                        if kulcsszo not in szimbolumok:
                            szimbolumok.append(kulcsszo)

        if talalatok:
            self.resultArea.setText("🔮 Értelmezések:\n\n" + "\n".join(talalatok))
        else:
            self.resultArea.setText("❌ Nincs találat az álomszótárban.\n\n"
                                  f"Próbált kulcsszavak: {', '.join(minden_keresett_kifejezes)}\n\n"
                                  "Próbáld: ablak, ház, víz, kutya, stb.")

        # === MENTÉS JSON-BE ÉS TÁBLÁZAT FRISSÍTÉS ===
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

        # ─── PRASHNA HOROSZKÓP FRISSÍTÉS ───
        pixmap = self.generate_prashna_chart()
        # Itt már a generate elvégzi a belső mentést és a kirakást is!

        # ─── KOTTA ÉS AI PROMPT LÁNC FRISSÍTÉSE ───
        prompt_text = build_music_prompt(text, mood, keywords, szimbolumok)
        self.scoreInfo.setText(prompt_text)

        folder = self.get_output_folder()
        bázis_név = f"kotta_prompt_{idokod}"
        pdf_ut, png_ut = export_score_to_pdf_and_png(prompt_text, folder, bázis_név)

        if os.path.exists(png_ut):
            self.current_score_pixmap = QPixmap(png_ut)
            self.update_score_pixmap()
    def generate_prashna_chart(self):
        import pendulum
        from PyQt5.QtGui import QPixmap
        from PyQt5.QtCore import Qt
        from modulok import astro_core
        from modulok import draw

        lat = getattr(self, "prashna_latitude", 46.8572)
        lon = getattr(self, "prashna_longitude", 18.1533)

        now = pendulum.now("Europe/Budapest")

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

       # Horoszkóp generálása
        svg_res, png_res = draw.rajzol_del_indiai_horoszkop(
            planet_data=res["planet_data"],
            tithi=res["tithi"],
            horoszkop_nev=res["varga_code"]
        )
    
        # A horoszkóp kép kirakása (Ez most már teljesen külön fut, fixen meg fog jelenni!)
        if os.path.exists(png_res):
            self.current_prashna_pixmap = QPixmap(png_res)
            self.update_prashna_pixmap()
            print("✅ Horoszkóp sikeresen kirajzolva a felületre!")

        # ─── YANTRA KÉP BETÖLTÉSE A KÜLÖN FÜLRE ───
        raw_tithi = res.get("tithi", "13")
        tithi_clean = str(raw_tithi).lower().strip()
        tithi_szam = 13

        if "trayodashi" in tithi_clean or "13" in tithi_clean: tithi_szam = 13
        elif "chaturdashi" in tithi_clean or "14" in tithi_clean: tithi_szam = 14
        elif "purnima" in tithi_clean or "15" in tithi_clean: tithi_szam = 15
        elif "ekadashi" in tithi_clean or "11" in tithi_clean: tithi_szam = 11
        elif "dvadashi" in tithi_clean or "12" in tithi_clean: tithi_szam = 12

        # Lekérjük a yantra elérési útját a fixált funkcióval
        yantra_fajl = astro_core.find_yantra_by_tithi(tithi_szam)
        
        if yantra_fajl and os.path.exists(yantra_fajl) and not os.path.isdir(yantra_fajl):
            try:
                yantra_pix = QPixmap(yantra_fajl)
                if not yantra_pix.isNull():
                    self.yantra_label.setPixmap(yantra_pix.scaled(550, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    self.yantra_label.setStyleSheet("background-color: #FFA500; border: 3px solid green; padding: 10px;")
                    print(f"🔮 Yantra sikeresen kirakva a fülre: {yantra_fajl}")
            except Exception as e:
                print(f"❌ Nem sikerült betölteni a yantra pixmapot: {e}")
        else:
            print(f"⚠️ Yantra képfájl nem található az új útvonalon: {yantra_fajl}")
            self.yantra_label.setStyleSheet("background-color: #FFA500; border: 3px solid red;")

        return self.current_prashna_pixmap
    def update_prashna_pixmap(self):
        if not self.current_prashna_pixmap:
            return
        scaled = self.current_prashna_pixmap.scaled(
            self.prashnaLabel.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
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

        # ✅ JAVÍTVA: belső függvények helyesen behúzva a show_coord_panel-en belülre
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
        # Kis késleltetéssel vagy közvetlenül frissítjük a pixmapot az aktuális mérethez igazítva
        if self.current_prashna_pixmap:
            self.update_prashna_pixmap()
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget
)
from gui.rashi_widget import RasiWidget
from gui.varshaphala_widget import VarshaphalaWidget
from gui.prashna_widget import PrashnaWidget
from gui.dasa_widget import DasaWidget
from gui.dreamy_widget import DreammyWidget

class MainGui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌌 SonicJyotish – Főkapu")
        self.setGeometry(100, 100, 1000, 700)
        self.initUI()

    def initUI(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        nav_layout = QHBoxLayout()

        # Navigációs gombok
        self.rasiButton = QPushButton("🔮 Rasi horoszkóp - Születési horoszkóp")
        self.varshaButton = QPushButton("🌞 Varshaphala - Éves horoszkóp")
        self.prashnaButton = QPushButton("📍 Prashna – kérdés pillanata")
        self.dasaButton = QPushButton("🌀 Dasa mandala")
        self.dreammyButton = QPushButton("🌠 Dreammy – Álomnapló")

        for btn in [self.rasiButton, self.varshaButton, self.prashnaButton,
                    self.dasaButton, self.dreammyButton]:
            nav_layout.addWidget(btn)

        # Widgetek
        self.stack = QStackedWidget()
        self.rasi_widget = RasiWidget()
        self.varsha_widget = VarshaphalaWidget(self.rasi_widget.get_birth_data())
        self.prashna_widget = PrashnaWidget()
        self.dasa_widget = DasaWidget(self.rasi_widget.get_planet_positions())
        self.dreammy_widget = DreammyWidget()

        for w in [self.rasi_widget, self.varsha_widget,
                  self.prashna_widget, self.dasa_widget, self.dreammy_widget]:
            self.stack.addWidget(w)

        # Gombok összekötése
        self.rasiButton.clicked.connect(lambda: self.stack.setCurrentWidget(self.rasi_widget))
        self.varshaButton.clicked.connect(lambda: self.stack.setCurrentWidget(self.varsha_widget))
        self.prashnaButton.clicked.connect(lambda: self.stack.setCurrentWidget(self.prashna_widget))
        self.dasaButton.clicked.connect(lambda: self.stack.setCurrentWidget(self.dasa_widget))
        self.dreammyButton.clicked.connect(lambda: self.stack.setCurrentWidget(self.dreammy_widget))

        # Layout összeállítás
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.stack)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

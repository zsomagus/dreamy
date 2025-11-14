import sys
from PyQt5.QtWidgets import QApplication
from gui.maingui import MainGui

app = QApplication(sys.argv)
window = MainGui()
window.show()
sys.exit(app.exec_())

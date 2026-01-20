import sys
from PyQt5.QtWidgets import QApplication
from gui.dreamy_widget import DreammyWidget

def main():
    app = QApplication(sys.argv)
    widget = DreammyWidget()
    widget.setWindowTitle("🌌 Dreamy Widget")
    widget.resize(600, 400)
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

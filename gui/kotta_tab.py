from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

def createScoreTab(parent):
    widget = QWidget()
    layout = QVBoxLayout(widget)

    parent.scoreInfo = QTextEdit()
    parent.scoreInfo.setReadOnly(True)
    layout.addWidget(parent.scoreInfo)

    parent.scorePreview = QLabel()
    parent.scorePreview.setAlignment(Qt.AlignCenter)
    layout.addWidget(parent.scorePreview)

    parent.generateScoreButton = QPushButton("Kotta generálása PDF-ben")
    parent.generateScoreButton.clicked.connect(parent.generate_score)
    layout.addWidget(parent.generateScoreButton)

    return widget


def generate_score(self):
    text = self.dreamText.toPlainText().strip()
    mood = self.moodSelector.currentText().strip()
    keywords = self.keywordInput.text().strip()

    prompt = build_music_prompt(text, mood, keywords, [])

    score = generate_full_score(prompt)

    folder = self.get_output_folder()
    base = "kotta_" + pendulum.now().format("YYYY-MM-DD_HHmmss")

    pdf_path, png_path = export_score_to_pdf_and_png(score, folder, base)

    self.scoreInfo.setText(f"Kotta elkészült:\n{pdf_path}")

    pix = QPixmap(png_path)
    self.scorePreview.setPixmap(
        pix.scaled(600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    )

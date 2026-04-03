from PySide6.QtWidgets import QMainWindow, QPushButton
class ButtonHolder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Button Holder App')
        button = QPushButton("Press Me")

        self.setCentralWidget(button)
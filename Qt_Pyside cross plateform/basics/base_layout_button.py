#Version 1
"""
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys
app =QApplication(sys.argv)

win = QMainWindow()
win.setWindowTitle('First Window')

button = QPushButton()
button.setText('Press Me')

win.setCentralWidget(button)
win.show()

app.exec()
"""
#Version 2
"""
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys
class ButtonHolder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Button Holder App')
        button = QPushButton("Press Me")

        self.setCentralWidget(button)


app = QApplication(sys.argv)

window = ButtonHolder()
window.show()
app.exec()
"""
#Version 3

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys
from button_holder import ButtonHolder
app = QApplication(sys.argv)

window = ButtonHolder()
window.show()
app.exec()
#Version 1
"""
from PySide6.QtWidgets import QApplication, QPushButton
import sys

def button_clicked():
    print('you pressed the button, didn\'t you')

app = QApplication(sys.argv)
button = QPushButton('Press Me')
button.clicked.connect(button_clicked)
button.show()
app.exec()
"""
#Version 2
"""
from PySide6.QtWidgets import QApplication, QPushButton
import sys
def button_clicked(data):
    print('you pressed the button, didn\'t you', data)

app = QApplication(sys.argv)
button = QPushButton('Press Me')
button.setCheckable(False)
button.clicked.connect(button_clicked)
button.show()
app.exec()
"""

#Version 3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QSlider
import sys
def respond_to_slider(data):
    print('slider moved to : ', data)

app = QApplication()
slider = QSlider(Qt.Horizontal)
slider.setMinimum(1)
slider.setMaximum(100)
slider.setValue(25)

slider.valueChanged.connect(respond_to_slider)
slider.show()
app.exec()
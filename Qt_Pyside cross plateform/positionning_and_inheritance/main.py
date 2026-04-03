from PySide6.QtWidgets import QApplication
import sys
from rockwidget import RocWidget

app = QApplication()
window = RocWidget()
window.show()
app.exec()
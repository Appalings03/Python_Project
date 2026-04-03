from PySide6.QtWidgets import QApplication, QMainWindow,QToolBar
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction,QIcon

class MainWindow(QMainWindow):
    def __init__(self,app):
        super().__init__()
        self.app = app
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Custom MainWindow')

        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')
        quit_action = file_menu.addAction('Quit')
        quit_action.triggered.connect(self.quit_app)

        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction('Copy')
        edit_menu.addAction('Cut')
        edit_menu.addAction('Paste')
        edit_menu.addAction('Undo')
        edit_menu.addAction('Redo')

        menubar.addMenu('Window')
        menubar.addMenu('Settings')
        menubar.addMenu('Help')

        toolbar = QToolBar("My main toolbar")
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)
        toolbar.addAction(quit_action)

        action1 = QAction("Some Action", self)
        action1.setStatusTip("Status message for some action")
        action1.triggered.connect(self.toolbar_button_clicked)
        toolbar.addAction(action1)

        action2 = QAction(QIcon("start.png"),"Some other Action", self)
        action2.setStatusTip("Status message for some other action")
        action2.triggered.connect(self.toolbar_button_clicked)
        action2.setCheckable(True)
        toolbar.addAction(action2)

    def quit_app(self):
        self.app.quit()
    
    def toolbar_button_clicked(self):
        print("Action triggered")
import sys
import os
import functools

try:
    # import the main window object (mw) from aqt
    from aqt import mw
    # import the "show info" tool from utils.py
    from aqt.utils import showInfo
    # import all of the Qt GUI library
    from aqt.qt import *
except:
    from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, QGridLayout, QLabel, QButtonGroup
    from PyQt5.QtGui import QIcon, QPixmap
    from PyQt5.QtGui import QIcon, QColor
    from PyQt5.QtCore import pyqtSlot

#test
from random import randrange

class UI(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Generic Language Tool'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(True)

        self.createFrovoGridLayout()
        self.createGridLayout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox2)
        windowLayout.addWidget(self.horizontalGroupBox)

        self.setLayout(windowLayout)
 
        self.show()


    @pyqtSlot()
    def on_click(self):
        print("clicked")

    def print_some(self, event, source_object=None):
        print("Clicked, from", source_object)
        print(source_object.filename)

    def print_id(self, event, source_object=None):
        print("Clicked, from", source_object)
        source_object.toggle()
        print(source_object.forvo_id)

    def createGridLayout(self):
        self.horizontalGroupBox = QGroupBox("Images")

        layout = QGridLayout()


        for row in range(0,3):
            for col in range(0,3):
                label = QLabel(self)
                #pixmap = QPixmap('../../addons21/GenericLanguageHelper/user_files/dog.jpg').scaledToWidth(256)
                pixmap = QPixmap('user_files/dog.jpg').scaledToWidth(200)
                #dir_path = os.path.dirname(os.path.realpath(__file__))
                #cwd = os.getcwd()
                #showInfo(cwd)
                label.setPixmap(pixmap)
                #label.setStyleSheet("QLabel { background-color : red; color : blue; }");
                label.filename = "row" + str(row) + " col" + str(col)
                label.mousePressEvent = functools.partial(self.print_some, source_object=label)
                layout.addWidget(label,row,col)
 
        self.horizontalGroupBox.setLayout(layout)


    def createFrovoGridLayout(self):
        self.horizontalGroupBox2 = QGroupBox("Audio")
        layout = QGridLayout()
        # layout.setColumnStretch(1, 4)
        # layout.setColumnStretch(2, 4)

        for col in range(0,5):
            r = randrange(10000,90000)
            button = QPushButton(str(r))
            button.forvo_id = r
            button.mousePressEvent = functools.partial(self.print_id, source_object=button)
            #button.clicked.connect(self.on_click)
            button.setCheckable(True)
            self.btn_grp.addButton(button)
            layout.addWidget(button, 0, col)

        self.horizontalGroupBox2.setLayout(layout)


def connectUI():
    global __window
    __window = UI()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UI()
    sys.exit(app.exec_())

else:
    # create a new menu item, "test"
    action = QAction("Generic Language Tool", mw)
    # set it to call testFunction when it's clicked
    action.triggered.connect(connectUI)

    # and add it to the tools menu
    mw.form.menuTools.addAction(action)
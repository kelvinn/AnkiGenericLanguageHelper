import sys
import os
import functools

import sys
sys.path.append("/Users/kelvin/Workspace/anki")


# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *

from random import randrange


class UI(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Generic Language Tool'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100
        self.note_ids = None
        self.current_note_id = None
        self.word_field = None
        self.image_field = None
        self.audio_field = None
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.note_ids = self.getTagsWithGLT()
        self.current_note_id = self.note_ids[0]

        config = mw.addonManager.getConfig(__name__)
        self.word_field = config['word_field']
        self.audio_field = config['audio_field']
        self.image_field = config['image_field']

        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(True)

        self.createFrovoGridLayout()
        self.createImageGridLayout()
        self.createWordTextBoxLayout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBoxWord)
        windowLayout.addWidget(self.horizontalGroupBoxAudio)
        windowLayout.addWidget(self.horizontalGroupBoxImages)


        button_next = QPushButton("Save")

        windowLayout.addWidget(button_next)
        self.setLayout(windowLayout)
 
        self.show()

    def getTagsWithGLT(self):
        ids = mw.col.findNotes("tag:glt")
        return ids

    @pyqtSlot()
    def on_click(self):
        print("clicked")

    def print_some(self, event, source_object=None, labels=None):
        print("Clicked, from", source_object)
        #source_object.palette().highlight().color().name()
        for label in labels:
            label.setStyleSheet("QLabel { padding: 4px;}")
        source_object.setStyleSheet("QLabel { background-color : red; color : blue; } QLabel { padding: 4px; }")
        #source_object.setStyleSheet("QLabel{background:transparent}")

        print(source_object.filename)

    def print_id(self, event, source_object=None):
        print("Clicked, from", source_object)
        source_object.toggle()
        ids = mw.col.findNotes("tag:glt")
        #for id in ids:
        #    note = mw.col.getNote(id)
        #    note.delTag("glt")
        #    note.flush()


        #showInfo(str(dir(card)))
        print(source_object.forvo_id)

    def createWordTextBoxLayout(self):
        self.horizontalGroupBoxWord = QGroupBox("Word")

        note = mw.col.getNote(self.current_note_id)

        note_items = dict(note.items())
        layout = QGridLayout()
        textbox = QLineEdit(self)
        textbox.setText(str(note_items[self.word_field]))
        textbox.resize(280, 40)

        layout.addWidget(textbox)

        self.horizontalGroupBoxWord.setLayout(layout)


    def createFrovoGridLayout(self):
        self.horizontalGroupBoxAudio = QGroupBox("Audio")
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

        self.horizontalGroupBoxAudio.setLayout(layout)


    def createImageGridLayout(self):
        self.horizontalGroupBoxImages = QGroupBox("Images")

        layout = QGridLayout()
        labels = []

        for row in range(0,3):
            for col in range(0,3):
                label = QLabel(self)
                pixmap = QPixmap('../../addons21/GenericLanguageHelper/user_files/dog.jpg').scaledToWidth(200)
                #pixmap = QPixmap('user_files/dog.jpg').scaledToWidth(200)
                #dir_path = os.path.dirname(os.path.realpath(__file__))
                #cwd = os.getcwd()
                #showInfo(cwd)
                defaultHLBackground = "#%02x%02x%02x" % label.palette().highlight().color().getRgb()[:3]
                defaultHLText = "#%02x%02x%02x" % label.palette().highlightedText().color().getRgb()[:3]


                label.setPixmap(pixmap)

                #label.setStyleSheet("QWidget:pressed { background:%s; color: %s;} QWidget { padding: 4px;}" % (
                #    defaultHLBackground, defaultHLText))

                #label.setStyleSheet("QLabel { background-color : red; color : blue; }");
                label.setStyleSheet("QLabel:hover { background:%s; color: %s;}" 
                                    "QLabel { padding: 4px;}" % (
                    defaultHLBackground, defaultHLText))

                #label.setStyleSheet("QLabel:active { background-color : red; color : blue; } QLabel { padding: 4px; }")
                labels.append(label)

                label.filename = "row" + str(row) + " col" + str(col)

                label.mousePressEvent = functools.partial(self.print_some, source_object=label, labels=labels)
                layout.addWidget(label,row,col)
 
        self.horizontalGroupBoxImages.setLayout(layout)





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
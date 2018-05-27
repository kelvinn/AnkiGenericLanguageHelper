import functools

# import the main window object (mw) from aqt
from aqt import mw

# import the "show info" tool from utils.py
from aqt.utils import showInfo

# import all of the Qt GUI library
from aqt.qt import *
from anki.sound import play
from random import randrange
from urllib.parse import quote
from .scraper import Forvo, GoogleImages


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
        self.current_note = None
        self.current_word = None
        self.word_field = None
        self.image_field = None
        self.audio_field = None
        self.forvo = Forvo()
        self.gi = GoogleImages()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.note_ids = self.get_tags_with_glt()
        if len(self.note_ids) > 0:
            self.current_note_id = self.note_ids[0]
        else:
            showInfo("No more notes!")
        self.current_note = mw.col.getNote(self.current_note_id)

        config = mw.addonManager.getConfig(__name__)
        self.word_field = config['word_field']
        self.audio_field = config['audio_field']
        self.image_field = config['image_field']

        note_items = dict(self.current_note.items())
        self.current_word = str(note_items[self.word_field])

        self.selected_image = None
        self.selected_audio = None

        self.btn_grp = QButtonGroup()
        self.btn_grp.setExclusive(True)

        self.create_forvo_grid_layout()
        self.create_image_grid_layout()
        self.create_word_textbox_layout()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBoxWord)
        windowLayout.addWidget(self.horizontalGroupBoxAudio)
        windowLayout.addWidget(self.horizontalGroupBoxImages)

        button_next = QPushButton("Save")
        button_next.mousePressEvent = functools.partial(self.next_card, source_object=button_next)

        windowLayout.addWidget(button_next)
        self.setLayout(windowLayout)
 
        self.show()

    def get_tags_with_glt(self):
        ids = mw.col.findNotes("tag:glt")
        return ids

    def next_card(self, event, source_object=None):
        audio_fname = mw.col.media.addFile(self.selected_audio)
        image_fname = mw.col.media.addFile(self.selected_image)

        self.current_note[self.audio_field] = u'[sound:%s]' % audio_fname
        self.current_note[self.image_field] = u'<img src="%s">' % image_fname
        self.current_note.delTag("glt")
        self.current_note.flush()
        self.note_ids = self.get_tags_with_glt()
        if len(self.note_ids) > 0:
            self.current_note_id = self.note_ids[0]
        else:
            showInfo("No more notes!")
        self.current_note = mw.col.getNote(self.current_note_id)
        note_items = dict(self.current_note.items())
        self.current_word = str(note_items[self.word_field])
        self.textbox.setText(self.current_word)
        self.populate_forvo_buttons()
        self.populate_image_layout()

    def save_image_selection(self, event, source_object=None, labels=None):
        for label in labels:
            label.setStyleSheet("QLabel { padding: 4px;}"
                                "QLabel { background-color : palette(window); color : blue; }")
        source_object.setStyleSheet("QLabel { background-color : red; color : blue; } QLabel { padding: 4px; }")
        self.selected_image = str(source_object.abs_image_path)

    def save_audio_selection(self, event, source_object=None):
        source_object.toggle()
        self.selected_audio = str(source_object.abs_audio_path)
        play(str(source_object.abs_audio_path))


    def create_word_textbox_layout(self):
        self.horizontalGroupBoxWord = QGroupBox("Word")
        layout = QGridLayout()
        self.textbox = QLineEdit(self)
        self.textbox.setText(self.current_word)
        self.textbox.resize(280, 40)

        layout.addWidget(self.textbox)

        self.horizontalGroupBoxWord.setLayout(layout)

    def populate_forvo_buttons(self):

        tags = self.current_note.tags
        try:
            lang = next((i for i in tags if i.startswith("lang"))).split('=')[1]
        except:
            lang = None

        num_audio_files = self.forvo.search(self.current_word, lang)
        for col in range(0, min(5, num_audio_files)):

            file_name = 'forvo_%s_%s.mp3' % (quote(self.current_word), col)
            audio_path = '../../addons21/GenericLanguageHelper/user_files/' + file_name
            abs_audio_path = os.path.abspath(audio_path)

            r = str(randrange(10000, 90000))

            button = QPushButton(r)
            button.forvo_id = randrange(10000, 90000)
            button.abs_audio_path = abs_audio_path
            button.audio_file_name = file_name
            button.mousePressEvent = functools.partial(self.save_audio_selection, source_object=button)
            # button.clicked.connect(self.on_click)
            button.setCheckable(True)
            self.btn_grp.addButton(button)
            self.forvo_layout.addWidget(button, 0, col)

    def create_forvo_grid_layout(self):
        self.horizontalGroupBoxAudio = QGroupBox("Audio")
        self.forvo_layout = QGridLayout()
        self.populate_forvo_buttons()
        self.horizontalGroupBoxAudio.setLayout(self.forvo_layout)

    def populate_image_layout(self):
        labels = []

        self.gi.search(self.current_word)
        image_counter = 0
        for row in range(0, 2):
            for col in range(0, 4):
                image_counter = image_counter + 1
                label = QLabel(self)
                image_path = '../../addons21/GenericLanguageHelper/user_files/%s.jpg' % image_counter
                pixmap = QPixmap(image_path).scaledToHeight(150)

                defaultHLBackground = "#%02x%02x%02x" % label.palette().highlight().color().getRgb()[:3]
                defaultHLText = "#%02x%02x%02x" % label.palette().highlightedText().color().getRgb()[:3]

                label.setPixmap(pixmap)
                label.setStyleSheet("QLabel:hover { background:%s; color: %s;}"
                                    "QLabel { background-color : palette(window); color : blue; }"
                                    "QLabel { padding: 4px; }" % (
                                        defaultHLBackground, defaultHLText))
                labels.append(label)

                label.filename = "row" + str(row) + " col" + str(col)
                label.abs_image_path = image_path

                label.mousePressEvent = functools.partial(self.save_image_selection, source_object=label, labels=labels)
                self.image_layout.addWidget(label, row, col)


    def create_image_grid_layout(self):
        self.horizontalGroupBoxImages = QGroupBox("Images")
        self.image_layout = QGridLayout()
        self.populate_image_layout()
        self.horizontalGroupBoxImages.setLayout(self.image_layout)


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
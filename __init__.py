# -*- encoding: utf-8 -*-
import functools

# import the main window object (mw) from aqt
from aqt import mw

# import the "show info" tool from utils.py
from aqt.utils import showInfo

# import all of the Qt GUI library
from aqt.qt import *
from anki.sound import play
from random import randrange
from .scraper import Forvo, BingImages, slugify
from time import sleep

USER_FILE_PATH = "../../addons21/AnkiGenericLanguageHelper/user_files/"


class Window(QProgressDialog):
    def __init__(self):
        QProgressDialog.__init__(self)
        self.setWindowTitle("Downloading Media")
        self.setLabelText("Downloading images and audio...")
        self.canceled.connect(self.close)
        self.setRange(0, 30)

    def start_fake_counter(self):
        for count in range(self.minimum(), self.maximum()):
            self.setValue(count)
            qApp.processEvents()
            sleep(0.15)


class DownloadThread(QThread):

    mySignal = pyqtSignal(list, list)

    def __init__(self, current_word, current_note, progress_window, image_text=None):
        super().__init__()
        self.current_word = current_word
        self.current_note = current_note
        self.image_text = image_text
        self.progress_window = progress_window
        self.forvo = Forvo()
        self.bi = BingImages()

    def run(self):

        tags = self.current_note.tags
        try:
            lang = next((i for i in tags if i.startswith("lang"))).split('=')[1]
        except:
            lang = None

        dl_image_filenames = self.bi.search(self.current_word, lang, image_text=self.image_text)
        dl_audio_filenames = self.forvo.search(self.current_word, lang)
        self.mySignal.emit(dl_audio_filenames, dl_image_filenames)


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
        self.extra_field = None
        self.extra_details = None
        self.selected_image = None
        self.selected_audio = None

        # Init once off UI components
        self.progress_window = Window()
        self.btn_grp = QButtonGroup()
        self.downloaded = DownloadThread(None, None, self.progress_window)
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.search_textbox = QLineEdit(self)

        self.forvo = Forvo()
        self.bi = BingImages()
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.note_ids = self.get_tags_with_glt()
        self.setMinimumWidth(750)
        if len(self.note_ids) > 0:
            self.current_note_id = self.note_ids[0]
        else:
            showInfo("No more notes tagged with 'glt'!")
            return

        self.current_note = mw.col.getNote(self.current_note_id)

        config = mw.addonManager.getConfig(__name__)
        self.word_field = config['word_field']
        self.audio_field = config['audio_field']
        self.image_field = config['image_field']
        self.extra_field = config['extra_field']

        note_items = dict(self.current_note.items())
        self.current_word = str(note_items[self.word_field])
        self.extra_details = str(note_items[self.extra_field])

        self.progress_window.setMinimumWidth(350)

        self.downloaded = DownloadThread(self.current_word, self.current_note, self.progress_window)
        self.downloaded.mySignal.connect(self.download_callback)

        self.selected_image = None
        self.selected_audio = None

        self.btn_grp.setExclusive(True)

        self.create_forvo_grid_layout()
        self.create_image_grid_layout()
        self.create_word_textbox_layout()

        windowlayout = QVBoxLayout()
        windowlayout.addWidget(self.horizontalGroupBoxWord)
        windowlayout.addWidget(self.horizontalGroupBoxAudio)
        windowlayout.addWidget(self.horizontalGroupBoxImages)

        self.hbox.addStretch(1)

        self.vbox.addStretch(1)
        self.vbox.addLayout(self.hbox)

        self.search_textbox.resize(300, 40)

        self.hbox.addWidget(self.search_textbox)

        button_search = QPushButton("Search")
        button_search.mousePressEvent = functools.partial(self.search_again, source_object=button_search)

        self.hbox.addWidget(button_search)

        button_skip = QPushButton("Skip")
        button_skip.mousePressEvent = functools.partial(self.skip_card, source_object=button_skip)

        self.hbox.addWidget(button_skip)

        button_next = QPushButton("Save")
        button_next.mousePressEvent = functools.partial(self.next_card, source_object=button_next)

        self.hbox.addWidget(button_next)

        windowlayout.addLayout(self.vbox)

        self.setLayout(windowlayout)
        self.progress_window.show()

        self.downloaded.start()
        self.progress_window.start_fake_counter()
        self.show()

    def get_tags_with_glt(self):
        ids = mw.col.findNotes("tag:glt")
        return ids

    @pyqtSlot(int)
    def on_resized(r):
        print('Circle was resized to radius %s.' % r)

    def search_again(self, event, source_object=None):
        # Kill thread if running
        if self.downloaded.isRunning():
            self.downloaded.terminate()

        self.current_note = mw.col.getNote(self.current_note_id)
        note_items = dict(self.current_note.items())
        self.current_word = str(note_items[self.word_field])
        self.extra_details = str(note_items[self.extra_field])

        self.downloaded = DownloadThread(current_word=self.current_word,
                                         current_note=self.current_note,
                                         progress_window=self.progress_window,
                                         image_text=self.search_textbox.text())

        self.downloaded.mySignal.connect(self.download_callback)
        self.downloaded.start()

        self.progress_window.show()
        self.progress_window.start_fake_counter()

    def skip_card(self, event, source_object=None):
        self.current_note.delTag("glt")
        self.current_note.flush()
        self.note_ids = self.get_tags_with_glt()
        if len(self.note_ids) > 0:
            self.current_note_id = self.note_ids[0]
        else:
            showInfo("No more notes tagged with 'glt'!")
            return

        self.progress_window.show()
        self.progress_window.start_fake_counter()

        self.search_textbox.setText("")
        self.current_note = mw.col.getNote(self.current_note_id)
        note_items = dict(self.current_note.items())
        self.current_word = str(note_items[self.word_field])
        self.extra_details = str(note_items[self.extra_field])

        # Kill thread if running
        if self.downloaded.isRunning():
            self.downloaded.terminate()

        self.downloaded = DownloadThread(self.current_word, self.current_note, self.progress_window)
        self.downloaded.mySignal.connect(self.download_callback)
        self.downloaded.start()

    @staticmethod
    def clean_user_data():
        import glob

        to_delete_files = glob.glob(USER_FILE_PATH + '/glt_*', recursive=True)

        for file_path in to_delete_files:
            try:
                os.remove(file_path)
            except OSError:
                print("Error while deleting file")

    def next_card(self, event, source_object=None):

        if self.selected_audio:

            audio_fname = mw.col.media.addFile(self.selected_audio)
            self.current_note[self.audio_field] = u'[sound:%s]' % audio_fname

        if self.selected_image:
            image_fname = mw.col.media.addFile(self.selected_image)
            self.current_note[self.image_field] = u'<img src="%s">' % image_fname

        self.search_textbox.setText("")

        self.current_note.delTag("glt")

        # Unsuspend card if it is suspended
        mw.col.sched.unsuspendCards([card.id for card in self.current_note.cards()])

        # Now we clean user data of any glt leftover files
        self.clean_user_data()

        self.current_note.flush()
        self.note_ids = self.get_tags_with_glt()
        if len(self.note_ids) > 0:
            self.current_note_id = self.note_ids[0]

        else:
            showInfo("No more notes tagged with 'glt'!")
            return

        self.selected_audio = None
        self.selected_image = None

        self.progress_window.show()
        self.progress_window.start_fake_counter()

        self.current_note = mw.col.getNote(self.current_note_id)
        note_items = dict(self.current_note.items())
        self.current_word = str(note_items[self.word_field])
        self.extra_details = str(note_items[self.extra_field])

        # Kill thread if running
        if self.downloaded.isRunning():
            self.downloaded.terminate()

        self.downloaded = DownloadThread(self.current_word, self.current_note, self.progress_window)
        self.downloaded.mySignal.connect(self.download_callback)
        self.downloaded.start()

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
        self.horizontalGroupBoxWord.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        layout = QGridLayout()

        newfont = QFont("Times", 22, QFont.Bold)

        self.word_label = QLabel(self)
        self.word_label.setText(self.current_word)
        self.word_label.setFont(newfont)

        self.word_label.setFixedWidth(100)
        self.word_label.setWordWrap(True);

        self.extra_detail_label = QLabel(self)
        self.extra_detail_label.setText(self.extra_details)
        self.hbox2 = QHBoxLayout()
        self.hbox2.setSpacing(10)
        self.hbox2.setDirection(QBoxLayout.LeftToRight)

        self.vbox2 = QVBoxLayout()

        self.vbox2.addLayout(self.hbox2)
        self.vbox2.setAlignment(Qt.AlignLeft)

        self.hbox2.addWidget(self.word_label)

        self.hbox2.addWidget(self.extra_detail_label)

        self.horizontalGroupBoxWord.setLayout(self.vbox2)

    @pyqtSlot(list, list)
    def download_callback(self, dl_audio_filenames, dl_image_filenames):

        self.word_label.setText(self.current_word)
        self.extra_detail_label.setText(self.extra_details)
        self.populate_image_layout(dl_image_filenames)
        self.populate_forvo_buttons(dl_audio_filenames)
        self.progress_window.hide()

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            widgetToRemove = layout.itemAt(i).widget()
            # remove it from the layout list
            layout.removeWidget(widgetToRemove)
            # remove it from the gui
            widgetToRemove.setParent(None)

    def populate_forvo_buttons(self, dl_audio_filenames):

        self.clear_layout(self.forvo_layout)
        for col in range(0, min(5, len(dl_audio_filenames))):

            file_name = slugify('glt_forvo_%s_%s' % (self.current_word, col)) + ".mp3"
            audio_path = '../../addons21/AnkiGenericLanguageHelper/user_files/' + file_name
            abs_audio_path = os.path.abspath(audio_path)

            r = str(randrange(10000, 90000))

            button = QPushButton(r)
            button.forvo_id = randrange(10000, 90000)
            button.abs_audio_path = abs_audio_path
            button.audio_file_name = file_name
            button.mousePressEvent = functools.partial(self.save_audio_selection, source_object=button)

            button.setCheckable(True)
            self.btn_grp.addButton(button)
            self.forvo_layout.addWidget(button, 0, col)

    def create_forvo_grid_layout(self):
        self.horizontalGroupBoxAudio = QGroupBox("Audio")
        self.forvo_layout = QGridLayout()
        self.horizontalGroupBoxAudio.setLayout(self.forvo_layout)

    def populate_image_layout(self, dl_image_filenames):
        labels = []
        image_counter = 0

        for row in range(0, 24):
            for col in range(0, 4):
                image_counter = image_counter + 1
                label = QLabel(self)
                label.setFixedWidth(158)
                file_name = slugify('glt_%s_%s' % (self.current_word, image_counter)) + ".jpg"
                image_path = f'{USER_FILE_PATH}' + file_name

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
        self.layout = QHBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)  # Set to make the inner widget resize with scroll area
        self.scrollArea.setMinimumHeight(400)
        self.scrollArea.setMinimumWidth(655)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setMinimumWidth(650)
        self.image_layout = QGridLayout(self.scrollAreaWidgetContents)
        self.horizontalGroupBoxImages.setMinimumWidth(680)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addWidget(self.scrollArea)
        self.horizontalGroupBoxImages.setLayout(self.layout)

    def create_button_layout(self):
        self.horizontalButtonBox = QHBoxLayout()


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

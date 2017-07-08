import sys

from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QLabel, QFileDialog,
                             QMessageBox, QPushButton, QHBoxLayout, QVBoxLayout,
                             QWidget, QShortcut, QStackedWidget)

class DisplayWidget(QLabel):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        self.closed.emit()

class Polo(QWidget):
    display_widget = None
    media_preview_stack = None

    def __init__(self):
        super().__init__()

        desktop_widget = QDesktopWidget()

        # Center master window
        self.resize(400, 200)
        self.center_widget(self, 0)

        # Create widgets
        self.display_widget = DisplayWidget()
        self.media_preview_stack = QStackedWidget()
        open_button = QPushButton("Open")
        clear_button = QPushButton("Clear")

        self.media_preview_stack.addWidget(QSvgWidget("blank.svg"))
        self.media_preview_stack.addWidget(QLabel())
        self.display_widget.setScaledContents(True)
        self.display_widget.setStyleSheet("background-color: rgb(20, 20, 20);")
        self.display_widget.closed.connect(self.close)
        open_button.clicked.connect(self.choose_media)
        clear_button.clicked.connect(self.clear_media)
        open_button.setToolTip("Choose a media file to display")
        clear_button.setToolTip("Clear the current media and turn off the display")

        # Set shortcuts
        open_shortcut = QShortcut(QKeySequence("O"), self)
        clear_shortcut = QShortcut(QKeySequence("C"), self)
        close_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        open_shortcut.activated.connect(self.choose_media)
        clear_shortcut.activated.connect(self.clear_media)
        close_shortcut.activated.connect(self.close)

        # Pack layouts
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        vbox.addStretch()
        vbox.addWidget(open_button)
        vbox.addWidget(clear_button)
        vbox.addStretch()

        hbox.addLayout(vbox)
        hbox.addWidget(self.media_preview_stack)

        hbox.setSpacing(30)
        hbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(10)

        # Create slave window
        if desktop_widget.screenCount() != 2:
            QMessageBox.warning(self, "Warning", "Cannot find a second screen, " \
                                                 "display will be on primary screen.")
            self.display_widget.resize(500, 500)
        else:
            self.center_widget(self.display_widget, 1)
            self.display_widget.showFullScreen()

        self.display_widget.show()

        self.setLayout(hbox)
        self.setWindowTitle("Polo")
        self.show()

    def choose_media(self):
        media = QFileDialog.getOpenFileName(self, "Select Media")
        if media:
            self.display_widget.setPixmap(QPixmap(media[0]))
            preview_label = self.media_preview_stack.widget(1)
            preview_label.setStyleSheet("border-image: url({0})".format(media[0]))
            self.media_preview_stack.setCurrentIndex(1)

    def clear_media(self):
        self.display_widget.clear()
        self.media_preview_stack.setCurrentIndex(0)

    def center_widget(self, widget, screen):
        frame = widget.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry(screen).center()
        frame.moveCenter(screen_center)
        widget.move(frame.topLeft())

    def closeEvent(self, event):
        self.display_widget.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    polo = Polo()

    sys.exit(app.exec_())

import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QLabel, QMessageBox,
                             QPushButton, QHBoxLayout, QVBoxLayout, QWidget)


class Polo(QWidget):
    media_preview = None
    display_widget = None

    def __init__(self):
        super().__init__()

        desktop_widget = QDesktopWidget()

        # Center master window
        self.resize(400, 200)
        self.center_widget(self, 0)

        # Create widgets
        self.display_widget = QLabel()
        self.media_preview = QSvgWidget("blank.svg")
        open_button = QPushButton("Open")
        clear_button = QPushButton("Clear")

        open_button.setToolTip("Choose a media file to display")
        clear_button.setToolTip("Clear the current media and turn off the display")

        # Pack layouts
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()

        vbox.addStretch()
        vbox.addWidget(open_button)
        vbox.addWidget(clear_button)
        vbox.addStretch()

        hbox.addLayout(vbox)
        hbox.addWidget(self.media_preview)

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

    def center_widget(self, widget, screen):
        frame = widget.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry(screen).center()
        frame.moveCenter(screen_center)
        widget.move(frame.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    polo = Polo()

    sys.exit(app.exec_())

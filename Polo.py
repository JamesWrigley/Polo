import sys
import argparse

from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt

from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QLabel, QFileDialog,
                             QMessageBox, QPushButton, QHBoxLayout, QVBoxLayout,
                             QWidget, QShortcut, QStackedWidget)

arg_parser = argparse.ArgumentParser("Polo")
arg_parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode (show bounding boxes)")
args = arg_parser.parse_args()

class DisplayWidget(QLabel):
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        self.closed.emit()

class Polo(QWidget):
    qmedia = None
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
            self.display_widget.showMaximized()
        else:
            self.center_widget(self.display_widget, 1)
            self.display_widget.showFullScreen()

        self.display_widget.show()

        self.setLayout(hbox)
        self.setWindowTitle("Polo")
        self.show()

    def choose_media(self):
        media_path = QFileDialog.getOpenFileName(self, "Select Media",
                                                 filter="Images (*.jpeg *.jpg *.png *.gif)")
        if media_path[0]:
            media = self.hologrify(Image.open(media_path[0]))
            self.qmedia = ImageQt(media)

            self.display_widget.setPixmap(QPixmap.fromImage(self.qmedia))
            preview_label = self.media_preview_stack.widget(1)
            preview_label.setStyleSheet("border-image: url({0})".format(media_path[0]))
            self.media_preview_stack.setCurrentIndex(1)

    def hologrify(self, media):
        # Dimensions of the screen, assuming `self.display_widget` is fullscreen
        center_length_mm = 100
        screen_width_mm = self.display_widget.widthMM()
        screen_height_mm = self.display_widget.heightMM()
        screen_width_px = self.display_widget.width()
        screen_height_px = self.display_widget.height()

        # Calculate the bounding box side length of each of the images
        x_media_length_mm = (screen_width_mm - center_length_mm) / 2
        y_media_length_mm = (screen_height_mm - center_length_mm) / 2
        media_length_mm = min(x_media_length_mm, y_media_length_mm)

        # Convert to pixels
        media_length_px = int(media_length_mm * self.display_widget.physicalDpiX() / 25.4)
        center_length_px = int(center_length_mm * self.display_widget.physicalDpiX() / 25.4)

        hologrified_media = Image.new("RGB", (screen_width_px, screen_height_px), (20, 20, 20))

        # Draw on the new image
        top = media.copy()
        top.thumbnail((media_length_px, media_length_px))
        top_x = int((screen_width_px - media_length_px) / 2)
        top_y = 0

        bottom = ImageOps.flip(top)
        bottom_x = top_x
        bottom_y = screen_height_px - media_length_px

        left = top.rotate(90, expand=True)
        left_x = 0
        left_y = media_length_px

        right = ImageOps.mirror(left)
        right_x = screen_width_px - media_length_px
        right_y = media_length_px

        # If in debug mode, draw the bounding boxes
        if args.debug:
            center = Image.new("RGB", (center_length_px, center_length_px), (255, 0, 0))
            bounding_box = Image.new("RGB", (media_length_px, media_length_px), (0, 128, 0))

            hologrified_media.paste(center, (int((screen_width_px - center_length_px) / 2),
                                             int((screen_height_px - center_length_px) / 2)))
            hologrified_media.paste(bounding_box, (top_x, top_y))
            hologrified_media.paste(bounding_box, (bottom_x, bottom_y))
            hologrified_media.paste(bounding_box, (left_x, left_y))
            hologrified_media.paste(bounding_box, (right_x, right_y))

        hologrified_media.paste(top, (top_x, top_y))
        hologrified_media.paste(bottom, (bottom_x, bottom_y))
        hologrified_media.paste(left, (left_x, left_y))
        hologrified_media.paste(right, (right_x, right_y))

        return hologrified_media

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

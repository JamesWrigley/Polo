import sys
import argparse

from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt

from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QLabel, QFileDialog,
                             QMessageBox, QPushButton, QHBoxLayout, QVBoxLayout,
                             QWidget, QShortcut, QStackedWidget)


# Parse command-line arguments
arg_parser = argparse.ArgumentParser("Polo")
arg_parser.add_argument("--debug", action="store_true",
                        help="Enable debug mode (show bounding boxes)")
args = arg_parser.parse_args()


class DisplayWidget(QLabel):
    """
    A subclass of QLabel that provides a closed() signal.
    """
    closed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def closeEvent(self, event):
        self.closed.emit()

class Polo(QWidget):
    # The hologrified media as a Qt-compatible object (i.e. ImageQt)
    qmedia = None

    # The widget in the slave window that displays `qmedia`
    display_widget = None

    # A QStackedWidget that holds both preview widgets, the first being a
    # QSvgWidget displaying the default preview image, and the second being a
    # QLabel that displays the users selected media.
    media_preview_stack = None

    def __init__(self):
        """
        Constructor for the main application class. Creates the GUI and sets up
        the initial state.
        """
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

        # Configure
        self.media_preview_stack.addWidget(QSvgWidget("blank.svg"))
        self.media_preview_stack.addWidget(QLabel())
        self.display_widget.setScaledContents(True)
        self.display_widget.setStyleSheet("background-color: rgb(20, 20, 20);")
        self.display_widget.closed.connect(self.close)

        # Set up connections
        open_button.clicked.connect(self.choose_media)
        clear_button.clicked.connect(self.clear_media)
        open_button.setToolTip("Choose a media file to display")
        clear_button.setToolTip("Clear the current media and turn off the display")

        # Set shortcuts
        open_shortcut = QShortcut(QKeySequence("O"), self, context=Qt.ApplicationShortcut)
        clear_shortcut = QShortcut(QKeySequence("C"), self, context=Qt.ApplicationShortcut)
        close_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self, context=Qt.ApplicationShortcut)
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

        self.display_widget.setWindowTitle("Polo - Display")
        self.display_widget.show()

        self.setLayout(hbox)
        self.setWindowTitle("Polo")
        self.show()

    def choose_media(self):
        """
        Open a dialog for the user to select a media file (currently only images
        are supported).
        """
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
        """
        Mirror the given media file in four directions for use as a hologram
        image. Note that the media is mirrored in the left side of the screen,
        leaving the right side to be used for some other purpose.
        """
        # Dimensions of the screen, assuming `self.display_widget` is fullscreen
        # and it is running on our TV. We need to hardcode some values for the TV
        # since Qt cannot obtain the correct ones by itself.
        center_length_mm = 100
        dpi = 68.84
        screen_width_mm = 701 # self.display_widget.widthMM()
        screen_height_mm = 398 # self.display_widget.heightMM()
        screen_width_px = self.display_widget.width()
        screen_height_px = self.display_widget.height()

        # Calculate the bounding box side length of each of the images, based
        # off the height because that's our limiting dimension.
        media_length_mm = (screen_height_mm - center_length_mm) / 2

        # Convert to pixels
        media_length_px = int(media_length_mm * dpi / 25.4)
        center_length_px = int(center_length_mm * dpi / 25.4)

        # Create the mirrored images, and calculate their locations
        top = media.copy()
        top.thumbnail((media_length_px, media_length_px))
        top_x = int((screen_height_px - top.width) / 2)
        top_y = int(((screen_height_px - center_length_px) / 2 - top.height) / 2)

        bottom = ImageOps.flip(top)
        bottom_x = top_x
        bottom_y = screen_height_px - top.height - top_y

        left = top.rotate(90, expand=True)
        left_x = top_y
        left_y = int((screen_height_px - left.height) / 2)

        right = ImageOps.mirror(left)
        right_x = screen_height_px - right.width - top_y
        right_y = left_y

        hologrified_media = Image.new("RGBA", (screen_width_px, screen_height_px), (0, 0, 0))

        # If in debug mode, draw the center square and bounding boxes
        if args.debug:
            hologram = Image.new("RGB", (screen_height_px, screen_height_px), (0, 157, 172))
            context = Image.new("RGB", (screen_height_px, screen_height_px), (173, 243, 0))
            center = Image.new("RGB", (center_length_px, center_length_px), (255, 0, 0))
            center_coord = int((screen_height_px - center_length_px) / 2)

            hologrified_media.paste(hologram, (0, 0))
            hologrified_media.paste(context, (screen_height_px, 0))
            hologrified_media.paste(center, (center_coord, center_coord))

        # Draw the mirrored images
        for img, corner in zip([top, bottom, left, right],
                                  [(top_x, top_y), (bottom_x, bottom_y),
                                   (left_x, left_y), (right_x, right_y)]):
            hologrified_media.paste(img, corner,
                                    img.split()[-1] if img.mode == "RGBA" else None)

        return hologrified_media

    def clear_media(self):
        """
        Reset the display widget to a solid color and the preview to the default
        SVG image (crosses).
        """
        self.display_widget.clear()
        self.media_preview_stack.setCurrentIndex(0)

    def center_widget(self, widget, screen):
        """
        Centers the given widget in the given screen.
        """
        frame = widget.frameGeometry()
        screen_center = QDesktopWidget().availableGeometry(screen).center()
        frame.moveCenter(screen_center)
        widget.move(frame.topLeft())

    def closeEvent(self, event):
        """
        An override to close the slave window when the master window closes.
        """
        self.display_widget.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    polo = Polo()

    sys.exit(app.exec_())

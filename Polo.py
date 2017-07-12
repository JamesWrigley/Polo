import sys
import argparse

from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt

from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QKeySequence, QPixmap
from PyQt5.QtWidgets import (QApplication, QCheckBox, QDesktopWidget, QLabel,
                             QLineEdit, QFileDialog, QLayout, QMessageBox,
                             QPushButton, QHBoxLayout, QVBoxLayout, QWidget,
                             QShortcut, QSizePolicy, QStackedWidget)


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
    # The input media
    media = None

    # The hologrified media as a Qt-compatible object (i.e. ImageQt)
    qmedia = None

    # The widget in the slave window that displays `qmedia`
    display_widget = None

    # A QStackedWidget that holds both preview widgets, the first being a
    # QSvgWidget displaying the default preview image, and the second being a
    # QLabel that displays the users selected media.
    media_preview_stack = None

    # Screen dimension widgets
    size_widget = None
    size_checkbox = None
    size_lineedit = None

    def __init__(self):
        """
        Constructor for the main application class. Creates the GUI and sets up
        the initial state.
        """
        super().__init__()

        # Center master window
        self.resize(400, 200)
        self.center_widget(self, 0)

        # Create widgets
        self.display_widget = DisplayWidget()
        self.media_preview_stack = QStackedWidget()
        open_button = QPushButton("Open")
        clear_button = QPushButton("Clear")
        preview_label = QLabel()

        self.size_widget = QWidget()
        self.size_checkbox = QCheckBox("Autosize")
        self.size_lineedit = QLineEdit("32")

        # Configure
        preview_label.setScaledContents(True)
        preview_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        open_button.setToolTip("Choose a media file to display")
        clear_button.setToolTip("Clear the current media and turn off the display")
        self.media_preview_stack.addWidget(QSvgWidget("blank.svg"))
        self.media_preview_stack.addWidget(preview_label)
        self.display_widget.setScaledContents(True)
        self.display_widget.setStyleSheet("background-color: rgb(20, 20, 20);")
        self.display_widget.closed.connect(self.close)
        self.size_lineedit.setInputMask("00 i\\n")
        self.size_checkbox.setChecked(True)
        self.size_checkbox.setToolTip("Use automatic screen dimensions for drawing")

        # Set up connections
        open_button.clicked.connect(self.choose_media)
        clear_button.clicked.connect(self.clear_media)
        self.size_checkbox.stateChanged.connect(self.set_dimensions_visibility)
        self.size_lineedit.editingFinished.connect(lambda: self.setFocus(Qt.OtherFocusReason))
        self.size_lineedit.editingFinished.connect(self.refresh)

        # Set shortcuts
        makeShortcut = lambda hotkey: QShortcut(QKeySequence(hotkey), self, context=Qt.ApplicationShortcut)
        open_shortcut = makeShortcut("O")
        clear_shortcut = makeShortcut("C")
        close_shortcut = makeShortcut("Ctrl+Q")
        dimensions_shortcut = makeShortcut("A")
        open_shortcut.activated.connect(self.choose_media)
        clear_shortcut.activated.connect(self.clear_media)
        close_shortcut.activated.connect(self.close)
        dimensions_shortcut.activated.connect(self.size_checkbox.toggle)

        # Pack layouts
        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        size_hbox = QHBoxLayout()

        size_hbox.addWidget(QLabel("Size:"))
        size_hbox.addWidget(self.size_lineedit)

        vbox.addWidget(open_button)
        vbox.addWidget(clear_button)
        vbox.addWidget(self.size_checkbox)
        vbox.addWidget(self.size_widget)
        vbox.addStretch()

        hbox.addLayout(vbox)
        hbox.addWidget(self.media_preview_stack)

        hbox.setSpacing(20)
        hbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(10)

        size_hbox.setContentsMargins(0, 0, 0, 0)
        self.size_widget.setLayout(size_hbox)

        # Create slave window
        desktop_widget = QDesktopWidget()
        if desktop_widget.screenCount() != 2:
            QMessageBox.warning(self, "Warning", "Cannot find a second screen, " \
                                                 "display will be on primary screen.")
            self.display_widget.showMaximized()
        else:
            self.center_widget(self.display_widget, 1)
            self.display_widget.showFullScreen()

        # Set default values in the screen dimension widgets
        display_geometry = desktop_widget.screenGeometry(self.display_widget)
        self.size_widget.hide()

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
            self.media = Image.open(media_path[0])
            self.qmedia = ImageQt(self.hologrify(self.media))
            self.refresh()

    def refresh(self):
        """
        [Re]loads the current media onto the preview widget and display window.
        """
        if self.media is not None:
            self.qmedia = ImageQt(self.hologrify(self.media))
            self.display_widget.setPixmap(QPixmap.fromImage(self.qmedia))
            self.media_preview_stack.widget(1).setPixmap(QPixmap.fromImage(ImageQt(self.media)))
            self.media_preview_stack.setCurrentIndex(1)

    def hologrify(self, media):
        """
        Mirror the given media file in four directions for use as a hologram
        image. Note that the media is mirrored in the left side of the screen,
        leaving the right side to be used for some other purpose.
        """
        center_length_mm = 100
        screen_width_px = self.display_widget.width()
        screen_height_px = self.display_widget.height()

        dpmm = -1 # Dots (i.e. pixels) per millimeter
        screen_width_mm = -1
        screen_height_mm = -1

        if self.size_checkbox.isChecked():
            dpmm = self.display_widget.physicalDpiX() / 25.4
            screen_width_mm = self.display_widget.widthMM()
            screen_height_mm = self.display_widget.heightMM()
        else:
            diagonal_length_mm = int(self.size_lineedit.text()[:2]) * 25.4
            dpmm = (screen_width_px**2 + screen_height_px**2)**0.5 / diagonal_length_mm
            screen_width_mm = screen_width_px / dpmm
            screen_height_mm = screen_height_px / dpmm

        # Calculate the bounding box side length of each of the images, based
        # off the height because that's our limiting dimension.
        media_length_mm = abs(screen_height_mm - center_length_mm) / 2

        # Convert to pixels
        media_length_px = int(media_length_mm * dpmm)
        center_length_px = int(center_length_mm * dpmm)

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

    def set_dimensions_visibility(self, state=None):
        self.refresh()
        self.size_widget.setVisible(not self.size_checkbox.isChecked())

if __name__ == "__main__":
    app = QApplication(sys.argv)

    polo = Polo()

    sys.exit(app.exec_())

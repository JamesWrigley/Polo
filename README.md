# Polo
A hologram image creator that [mirrors](http://jamesw.bio/images/polo.png) its
input for use in a right-frustum style hologram. Meant to be used with two
screens (one master, one slave).

```
usage: Polo [-h] [--debug]

optional arguments:
  -h, --help  show this help message and exit
  --debug     Enable debug mode (show bounding boxes)
```

Hotkeys:
* `O`: Open media file (images or videos).
* `C`: Clear current media.
* `N`: Go to the next media in the current directory.
* `P`: Go to the previous media in the current directory.
* `A`: Toggle automatic scaling. Polo attempts to automatically detect the DPI
       of the display device in order to correctly scale the images, but this is not
       always possible, so disabling automatic scaling will let the user enter
       the diagonal length of their display device (in inches).
* `Ctrl + Q`: Quit Polo.

## Requirements
* Python 3
* PyQt5
* Pillow
* imageio

Tested on Windows and Linux, in theory should work on OSX.

## Quickstart
This assumes that you have Python 3 installed and are in the cloned source
directory:

```bash
# Install dependencies (only need to run this once)
pip3 install --user pyqt5
pip3 install --user pillow
pip3 install --user imageio

# Run Polo
python3 Polo.py

```

Note that the Python 3 binary may just be called `python` on Windows and some
Linux distros (i.e. Arch Linux).

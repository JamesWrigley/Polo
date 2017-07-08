# Polo
A hologram image creator that mirrors its input for use in a right-frustum style
hologram. Meant to be used with two screens (one master, one slave).

```
usage: Polo [-h] [--debug]

optional arguments:
  -h, --help  show this help message and exit
  --debug     Enable debug mode (show bounding boxes)
```

Hotkeys:
* `O`: Open media file (currently only images are supported).
* `C`: Clear current media.
* `Ctrl + Q`: Quit Polo.

## Requirements
* Python 3
* PyQt5
* Pillow

Tested on Linux, in theory should work on Windows and OSX.

## Quickstart
This assumes that you have Python 3 installed and are in the cloned source
directory:

```bash
# Install dependencies (only need to run once)
pip3 install --user pyqt5
pip3 install --user pillow

# Run Polo
python3 Polo.py

```

Note that the Python 3 binary may just be called `python` on Windows and some
Linux distros (i.e. Arch Linux).

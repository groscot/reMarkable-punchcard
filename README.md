# Parsing reMarkable forms

The given example shows the base logic of how to automatically read "punch card forms" into Python. Works on exported PNGs from the reMarkable desktop app. Check the parameters and function `extract_page()` in `process_form.py` to apply it to your own form.

### Requirements

- numpy
- opencv (only to load the image, you can also replace with Pillow)
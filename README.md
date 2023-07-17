# Dynamic-Dictate
Automatic OCR-based document narrator
![Screenshot](https://raw.githubusercontent.com/suchithh/Dynamic-Dictate/main/res/screenshot.png)

## Summary:
Dynamic Dictate is a program that enables dynamic narration of text from a document using audio and visual cues extracted from the user's written page. It utilizes OpenCV for image processing and Tesseract for OCR (Optical Character Recognition).

## Dependencies:
1. Install python dependencies by running `pip install -r requirements.txt`
2. The Tesseract binary for 64-bit windows is included. The 32-bit binaries, if required, can be downloaded and installed from [here](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-v5.0.0-alpha.20210811.exe). Instructions to install tesseract for other operating systems can be found [here](https://tesseract-ocr.github.io/tessdoc/Installation.html).

## Usage:
1. Run `python ui_main.py` in the root directory.

## Additional Information:
Dynamic Dictate is designed to provide an automatic narration of text from a document by leveraging image processing and AI technologies. It introduces an alternative input method using pen and paper.

The primary objective of Dynamic Dictate is to accept PDF files as input and narrate the document using a Text-to-Speech approach on a line-by-line basis, tailored to the user's writing speed. To initiate the process, users need to point their webcam at the piece of paper they are currently writing on. In case video input is not available, users can rely on audio cues or use the spacebar to command the narrator to continue reading.

The program is designed to be used by people with visual impairments, dyslexia, or other reading disabilities. It can also be used by people who prefer to listen to the text rather than read it.
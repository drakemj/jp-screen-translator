# jp-screen-translator
## About
The main aim of this application is to take a portion of your screen from a specific monitor and translate japanese text, though you can easily modify the source code to translate from all kinds of languages. As to not be too burdensome on the system, this will take screenshots of the selected portion of a monitor at a configurable rate (to be added!), and provide a log.

## Usage
![image](https://github.com/user-attachments/assets/61af1dbd-549d-4b9a-98bd-4ebfc7ffae8e)
Select a monitor using the dropdown box above the screen preview, then select the portion of the screen to translate. Since image processing and OCR has to happen on the portion of the image you select, using the entire screen will take longer and will be much more CPU intensive. To start/stop the translation thread, you can use the buttons in the log window on the right hand side. Currently, the log holds up to 50 messages. You can update the capture area while the thread is running safely.

**Note*****\
Currently, the application uses a library which makes a Google Translate request, which is not backed by an API key. I've done my best to limit the amount of requests the application will make, but it is likely that you will encounter throttling, at which point you will stop getting any updates on the translation log. The best workaround I've found so far for this is to turn on a VPN/change IP, and restart the application entirely. I plan on looking into a better way around this. Additionally, the program has only been tested with white on black or black on white test.

## Installation
### Executable (Windows only)
In addition to getting the exectuable from the release on the right hand side, you must also have the major dependency of this project, Tesseract OCR, installed. The main repo can be found [here.](https://github.com/tesseract-ocr/tesseract)\
\
I recommend installing this specific binary (I haven't tried others) [here,](https://github.com/UB-Mannheim/tesseract/wiki), and make sure to install the Japanese language data through that installer, or you can get the trained data from the Tesseract repository. Note the installation directory, and add it to your PATH. (You can search "environmental variables" in your windows search bar, under System Properties > Advanced select "Environment Variables..." at the bottom, click edit under the **system** variables look for Path, click on it and edit, then make a **new** variable with the path to your binary, typically something like `C:\Program Files\Tesseract-OCR`.) \
\
You additionally may need to add the following system variable, and set it to the `tessdata` location in your install directory.\
![image](https://github.com/user-attachments/assets/dd7e6b20-54d4-4ecf-9fa8-315aa8ded9a5)\
This would likely be the case if you are selecting the capture area and starting translation, but no output is appearing. Will make this clearer through program output in the future (lazy.)


### Development
Use Python 3.9 or later. In the base directory of your cloned repo, you can install the required libraries with\
\
`pip install -r requirements.txt`\
\
and then run\
\
`python screen_translator.py`\
\
to run the program.

# Planned features
- better exception handling (high priority)
- more languages
- improved installation process
- more settings and save/load config
- conditionally hide/show capture area preview
- more!

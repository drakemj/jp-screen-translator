import threading
from mtranslate import translate
from PIL import Image as PILImage, ImageGrab
import pytesseract

from processing import *

TRANSLATE_DEBUG = 0

MIN_CROP_LENGTH = 10
GAUSSIAN_SIGMA = 10
GAUSSIAN_RADIUS = 100
UNSHARP_AMOUNT = 4


crop_vars = [0, 0, 0, 0]
crop_lock = threading.Lock()

def set_crop(input):
    crop_lock.acquire()
    for i in range(len(crop_vars)):
        crop_vars[i] = input[i]
    crop_lock.release()

def get_crop():
    output = [0, 0, 0, 0]
    crop_lock.acquire()
    for i in range(len(crop_vars)):
        output[i] = crop_vars[i]
    crop_lock.release()
    
    return output

import time

def translate_loop_func():
    while True:
        im = ImageGrab.grab(bbox=None, all_screens=True).convert("RGBA")
        im2 = process_image(im.crop(get_crop()), GAUSSIAN_SIGMA, GAUSSIAN_RADIUS, UNSHARP_AMOUNT)

        im_s = pytesseract.image_to_string(im2, lang='jpn').replace(" ", "")
        im_s = im_s.replace("\n", "").replace("*", "")
        if TRANSLATE_DEBUG:
            im2.show()
            print(im_s)
            return

        translatedText = translate(im_s, "en", "auto")
        print(translatedText)
        print("recalculating...")
        time.sleep(5)

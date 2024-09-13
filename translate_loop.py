import threading
from mtranslate import translate
from PIL import Image as PILImage, ImageGrab
import pytesseract
import difflib

from processing import *
from screen_translator import *

TRANSLATE_DEBUG = 0

MIN_CROP_LENGTH = 10
GAUSSIAN_SIGMA = 10
GAUSSIAN_RADIUS = 100
UNSHARP_AMOUNT = 4


crop_vars = [0, 0, 0, 0]
crop_lock = threading.Lock()
running = True

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

def stop_running():
    global running
    running = False

def resume_running():
    global running
    running = True
    
def count_different_characters(str1, str2):
    matcher = difflib.SequenceMatcher(None, str1, str2)
    matching_blocks = matcher.get_matching_blocks()
    
    differences = 0
    for i, block in enumerate(matching_blocks):
        if i == 0:
            differences += block.a
        else:
            prev_block = matching_blocks[i - 1]
            differences += (block.a - (prev_block.a + prev_block.size))
    
    last_block = matching_blocks[-1]
    differences += (len(str1) - (last_block.a + last_block.size))
    differences += (len(str2) - (last_block.b + last_block.size))
    
    return differences

# TODO: make this configurable
def guess_new_text(str1, str2):
    diff = count_different_characters(str1, str2)
    char_count = max(1, min(len(str1), len(str2)))
    if float(diff)/char_count > 0.15:
        return True
    return False

import time

def translate_loop_func(monitor):
    last = ""
    global running
    running = True

    while True:
        while running:
            im = ImageGrab.grab(bbox=(get_crop()), all_screens=True).convert("RGBA")
            im2 = process_image(im, GAUSSIAN_SIGMA, GAUSSIAN_RADIUS, UNSHARP_AMOUNT)

            im_s = pytesseract.image_to_string(im2, lang='jpn').replace(" ", "")
            im_s = im_s.replace("\n", "").replace("*", "")
            if TRANSLATE_DEBUG:
                im2.show()
                print(im_s)
                return

            if not guess_new_text(im_s, last):
                continue
            
            last = im_s
            translatedText = translate(im_s, "en", "auto")
            monitor.add_message(translatedText)

            time.sleep(1)
        while not running:
            time.sleep(2)

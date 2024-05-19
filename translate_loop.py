import threading
from mtranslate import translate
from PIL import Image as PILImage, ImageGrab

import pytesseract

# translation = translate("ちゃんとした人間なのかもしれねぇけど、あいつには欲望っていうもんがあってな", "en", "auto")
# print(translation)
# translatedText = translate("ちゃんとした人間にさえそういう願望があるもんだ", "en", "auto")
# print(translatedText)

# img_string = pytesseract.image_to_string('C:/users/drake/Desktop/image333.png', lang='jpn').replace(" ", "")
# img_string = img_string.replace("\'", "\'")
# img_string = img_string.replace("\n", "")
# print(img_string)
# translatedText = translate(img_string, "en", "auto")
# print(translatedText)

crop_vars = [0, 0, 0, 0]

crop_lock = threading.Lock()

def set_crop(input, maxes):
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

def translate_loop_func():
    while True:
        a = 0

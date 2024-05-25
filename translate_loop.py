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

MIN_CROP_LENGTH = 10

crop_vars = [0, 0, 0, 0]
crop_lock = threading.Lock()

def set_crop(input, maxes):
    for i, e in enumerate(maxes):
        input[i] = min(e, input[i])
        input[i] = max(input[i], MIN_CROP_LENGTH)
    input[2] = min(input[2], maxes[0]-input[0])
    input[3] = min(input[3], maxes[1]-input[1])

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

    output[0], output[1], output[2], output[3] = output[2], output[3], output[0] + output[2], output[1] + output[3]
    return output

def translate_loop_func():
    while True:
        a = 0

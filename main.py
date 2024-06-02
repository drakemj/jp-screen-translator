import threading
from PIL import Image as PILImage, ImageGrab, ImageTk, ImageFilter, ImageDraw
from tkinter import *
from tkinter import ttk

from translate_loop import *
from processing import *

# "defines"
CAPTURE_PREVIEW_HEIGHT = 300
BUTTON_SIZE_PX = 20
MIN_IMAGE_COLORVAL = 0
MAX_IMAGE_COLORVAL = 255

GAUSSIAN_SIGMA = 40
GAUSSIAN_RADIUS = 40
UNSHARP_AMOUNT = 7

# evil globals
main_thread = threading.Thread(target=translate_loop_func, daemon=True)
crop_max = [0, 0]

# ttk interpreter and window setup
root = Tk()
root.resizable(width=False, height=False)
i_p = PILImage.open(r"img/icon.png")
i_o = ImageTk.PhotoImage(i_p)
root.wm_iconphoto(True, i_o)
root.title("screen-translator")
frm = ttk.Frame(root, padding=10)
frm.grid(ipadx=90, ipady=60)

# get initial screenshot
capture = ImageGrab.grab(bbox=None, all_screens=True)
ratio = capture.height/CAPTURE_PREVIEW_HEIGHT
crop_max[0] = capture.width
crop_max[1] = capture.height
capture = capture.resize(size=[int(capture.width/ratio), int(capture.height/ratio)])
d_capture = ImageDraw.Draw(capture)
d_capture.rectangle([0, 0, capture.width, capture.height], outline="red", width=4)
capture_tk = ImageTk.PhotoImage(capture)

# gui (got bored figuring out alignment, no resizing for you!) definitely breaks with many monitors, etc.
preview_row = 0
ttk.Label(frm, text="Capture area preview", font=("Arial", "15", "bold")).grid(column=0, row=preview_row)
preview = ttk.Label(frm, image=capture_tk)
preview.grid(column=0, row=preview_row+1, columnspan=10)

crop_row = preview_row + 2
ttk.Label(frm, text="Cropping", font=("Arial", "15", "bold")).grid(column=0, row=crop_row)

crop_size_row = crop_row + 1
c_width, c_height, c_x_off, c_y_off = StringVar(), StringVar(), StringVar(), StringVar()
ttk.Label(frm, text="width").grid(column=0, row=crop_size_row)
ttk.Label(frm, text="height").grid(column=1, row=crop_size_row)
ttk.Entry(frm, textvariable=c_width).grid(column=0, row=crop_size_row+1)
ttk.Entry(frm, textvariable=c_height).grid(column=1, row=crop_size_row+1)

crop_off_row = crop_size_row + 2
ttk.Label(frm, text="xoff").grid(column=0, row=crop_off_row)
ttk.Label(frm, text="yoff").grid(column=1, row=crop_off_row)
ttk.Entry(frm, textvariable=c_x_off).grid(column=0, row=crop_off_row+1)
ttk.Entry(frm, textvariable=c_y_off).grid(column=1, row=crop_off_row+1)

def confirm_crop():
    input = []
    for s in [c_width, c_height, c_x_off, c_y_off]:
        input.append(int(s.get() if s.get() else 0))
    set_crop(input, crop_max)

    global capture_tk
    capture = ImageGrab.grab(bbox=None, all_screens=True)
    d_capture = ImageDraw.Draw(capture)

    crop = get_crop()
    d_capture.rectangle(crop, outline="red", width=2)
    capture = capture.resize(size=[int(capture.width/ratio), int(capture.height/ratio)])
    capture_tk = ImageTk.PhotoImage(capture)
    preview.configure(image=capture_tk)


def start_translate_loop():
    if not main_thread.is_alive():
        main_thread.start()

ttk.Button(frm, text="Confirm crop", width=BUTTON_SIZE_PX, command=confirm_crop).grid(column=2, row=crop_row+1)
ttk.Button(frm, text="Start Capture", width=BUTTON_SIZE_PX, command=start_translate_loop).grid(column=2, row=crop_row+2)
ttk.Button(frm, text="Exit program", width=BUTTON_SIZE_PX, command=root.destroy).grid(column=2, row=crop_row+3)

im = PILImage.open(r"img/input/image3.png")
im2 = process_image(im, GAUSSIAN_SIGMA, GAUSSIAN_RADIUS, UNSHARP_AMOUNT)
print(im2.height, im2.width)
im3 = im2.convert('L')
im3.show()

im4 = im.convert('L')

total = 0.0
for i in range(im3.height):
    for j in range(im3.width):
        total += im3.getpixel([j, i])

print("average across gaussian: {0}".format(total/(im3.height*im3.width)))

print(im2.getpixel([500, 500]))
print(im3.getpixel([500, 500]))

print(im2.width, im2.height, im.width, im.height)

print(type(im))
s_channel = im.convert('L')
s_channel.save(r"img/input/image35.png")

amount = UNSHARP_AMOUNT
for i in range(s_channel.height):
    for j in range (s_channel.width - 1):
        o = im4.getpixel([j, i])
        b = im3.getpixel([j, i])

        for k in range(3):
            r = o + (o - b) * amount
            r = min(MAX_IMAGE_COLORVAL, max(r, MIN_IMAGE_COLORVAL))

        im4.putpixel([j, i], r)

im4.show()

import pytesseract
img_string = pytesseract.image_to_string(s_channel, lang='jpn').replace(" ", "")
print(img_string)

root.mainloop()

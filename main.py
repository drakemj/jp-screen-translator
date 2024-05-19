from mtranslate import translate
from PIL import Image as PILImage, ImageGrab, ImageTk
from tkinter import *
from tkinter import ttk

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

# evil globals

# "defines"
CAPTURE_PREVIEW_HEIGHT = 175

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
capture.save(r"img/input/capture.png")
ratio = capture.height/CAPTURE_PREVIEW_HEIGHT
capture = capture.resize(size=[int(capture.width/ratio), int(capture.height/ratio)])
capture_tk = ImageTk.PhotoImage(capture)

# gui (got bored figuring out alignment, no resizing for you!) definitely breaks with many monitors, etc.
preview_row = 0
ttk.Label(frm, text="Capture area preview", font=("Arial", "15", "bold")).grid(column=0, row=preview_row)
ttk.Label(frm, image=capture_tk).grid(column=0, row=preview_row+1, columnspan=10)

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

ttk.Button(frm, text="Confirm crop", command=root.destroy).grid(column=2, row=crop_row+1)
ttk.Button(frm, text="Start Capture", command=root.destroy).grid(column=2, row=crop_row+2)
ttk.Button(frm, text="Exit program", command=root.destroy).grid(column=2, row=crop_row+3)

root.mainloop()

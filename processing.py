from PIL import Image
import numpy as np

import math

DEBUG_PROCESSING = 0

GS_RC_WEIGHT = 0.299
GS_GC_WEIGHT = 0.587
GS_BC_WEIGHT = 0.114
FONTC_WEIGHT = 0.50

NUM_CHANNELS = 3

def gaussian_weight(x, y, s):
    c = 1/(math.sqrt(2*math.pi) * s)
    arg = -(x**2 + y**2)/(2 * s**2)
    return c * math.exp(arg)

def generate_gaussian(radius, sigma):
    n = radius*2 + 1
    o = [[0.0 for i in range(n)] for j in range(n)]

    total_weight = 0.0
    for i in range(n):
        for j in range(n):
            o[i][j] = w = gaussian_weight(i, j, sigma)
            total_weight += w
    for i in range(n):
        for j in range(n):
            o[i][j] /= total_weight

    return o

# applies an unsharp mask to the image and returns it
def process_image(image, sigma, radius, amount, text_color=255):
    im = np.array(image)
    pad_im = np.pad(im, ((radius, radius), (radius, radius), (0, 0)), mode='reflect')

    gaussian = generate_gaussian(radius, sigma)
    gaussian = np.array(gaussian)

    o = []
    channels = np.split(pad_im, NUM_CHANNELS + 1, axis=2)  # ignore alpha
    for c in range(NUM_CHANNELS):
        a = np.reshape(channels[c], [len(pad_im), len(pad_im[0])])
        z = np.fft.irfft2(np.fft.rfft2(a) * np.fft.rfft2(gaussian, a.shape))
        o.append(z)
    o = np.array([o[i] for i in range(NUM_CHANNELS)])
    o = np.transpose(o, (1, 2, 0))

    # after applying filters separately for each channel, shift the single-channel
    # output gaussian towards the grayscale text font value anyways. keeping multiple channels
    # in case I want to unsharp separately later and do some other processing.
    o = np.pad(o, ((0, 0), (0, 0), (0, 1)), constant_values=text_color)
    w_rem = 1 - FONTC_WEIGHT
    o = np.average(o, axis=2, weights=(w_rem*GS_RC_WEIGHT, w_rem*GS_GC_WEIGHT, w_rem*GS_BC_WEIGHT, FONTC_WEIGHT))

    s = o.shape
    o = o[radius:s[0]-radius,radius:s[1]-radius].astype(np.uint8)
    gray_im = np.average(im, axis=2, weights=(GS_RC_WEIGHT, GS_GC_WEIGHT, GS_BC_WEIGHT, 0))

    gray_s = gray_im.shape
    gaussian_s = o.shape
    if gray_s != gaussian_s and DEBUG_PROCESSING:
        print("disagreement in gaussian dimensions, continuing...")
    
    for i in range(min(gray_s[0], gaussian_s[0])):
        for j in range(min(gray_s[1], gaussian_s[1])):
            g = gray_im[i][j]
            g = g + (g - o[i][j])*amount
            o[i][j] = max(0, min(255, g))

    return Image.fromarray(o)
                
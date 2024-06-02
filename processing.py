from PIL import Image
import numpy as np

import math


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
def process_image(image, sigma, radius, amount):
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
    o = np.transpose(o, [1, 2, 0])

    return Image.fromarray(o.astype(np.uint8))
                
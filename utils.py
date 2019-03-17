"""
Some codes from https://github.com/Newmu/dcgan_code
"""
from __future__ import division
import math
import json
import random
import pprint
import scipy.misc
import numpy as np
from time import gmtime, strftime

pp = pprint.PrettyPrinter()

get_stddev = lambda x, k_h, k_w: 1/math.sqrt(k_w*k_h*x.get_shape()[-1])

# -----------------------------
# new added functions for pix2pix

def load_data(image_path, flip=True, is_test=False, fine_size=256):
    img_A, img_B = load_image(image_path)
    img_A, img_B = preprocess_A_and_B(img_A, img_B, fine_size=fine_size, flip=flip, is_test=is_test)

    img_A = img_A/127.5 - 1.
    img_B = img_B/127.5 - 1.

    img_AB = np.concatenate((img_A, img_B), axis=2)
    # img_AB shape: (fine_size, fine_size, input_c_dim + output_c_dim)
    return img_AB

def preprocess_img(img):
    w = int(img.shape[1])
    w2 = int(w/2)
    img_A = img[:, 0:w2]
    img_B = img[:, w2:w]

    img_A = img_A/127.5 - 1.
    img_B = img_B/127.5 - 1.

    img_AB = np.concatenate((img_A, img_B), axis=2)
    # img_AB shape: (fine_size, fine_size, input_c_dim + output_c_dim)
    return img_AB

def load_image(image_path):
    input_img = imread(image_path)
    w = int(input_img.shape[1])
    w2 = int(w/2)
    img_A = input_img[:, 0:w2]
    img_B = input_img[:, w2:w]

    return img_A, img_B

def preprocess_A_and_B(img_A, img_B, load_size=286, fine_size=256, flip=True, is_test=False):
    if is_test:
        img_A = scipy.misc.imresize(img_A, [fine_size, fine_size])
        img_B = scipy.misc.imresize(img_B, [fine_size, fine_size])
    else:
        img_A = scipy.misc.imresize(img_A, [fine_size, fine_size])
        img_B = scipy.misc.imresize(img_B, [fine_size, fine_size])
        # img_A = scipy.misc.imresize(img_A, [load_size, load_size])
        # img_B = scipy.misc.imresize(img_B, [load_size, load_size])
        #
        # h1 = int(np.ceil(np.random.uniform(1e-2, load_size-fine_size)))
        # w1 = int(np.ceil(np.random.uniform(1e-2, load_size-fine_size)))
        # img_A = img_A[h1:h1+fine_size, w1:w1+fine_size]
        # img_B = img_B[h1:h1+fine_size, w1:w1+fine_size]

        if flip and np.random.random() > 0.5:
            img_A = np.flipud(img_A)
            img_B = np.flipud(img_B)

    return img_A, img_B

# -----------------------------

def get_image(image_path, image_size, is_crop=True, resize_w=64, is_grayscale = False):
    return transform(imread(image_path, is_grayscale), image_size, is_crop, resize_w)

def save_images(images, size, image_path):
    return imsave(inverse_transform(images), size, image_path)

def imread(path, is_grayscale = False):
    if (is_grayscale):
        return scipy.misc.imread(path, flatten = True).astype(np.float)
    else:
        return scipy.misc.imread(path).astype(np.float)

def merge_images(images, size):
    return inverse_transform(images)

def merge(images, size):
    h, w = images.shape[1], images.shape[2]
    img = np.zeros((h * size[0], w * size[1], 3))
    for idx, image in enumerate(images):
        i = idx % size[1]
        j = idx // size[1]
        img[j*h:j*h+h, i*w:i*w+w, :] = image

    return img

def imsave(images, size, path):
    return scipy.misc.imsave(path, merge(images, size))

def transform(image, npx=64, is_crop=True, resize_w=64):
    # npx : # of pixels width/height of image
    if is_crop:
        cropped_image = center_crop(image, npx, resize_w=resize_w)
    else:
        cropped_image = image
    return np.array(cropped_image)/127.5 - 1.

def inverse_transform(images):
    return (images+1.)/2.

def rot90_batch(arrs, *args, **kwargs):
    batch = []
    for arr in arrs:
        batch.append(np.rot90(arr, *args, **kwargs))
    return np.stack(batch, axis=0)

def imresize_batch(arrs, *args, **kwargs):
    batch = []
    for arr in arrs:
        batch.append(scipy.misc.imresize(arr, *args, **kwargs))
    return np.stack(batch, axis=0)

def resize_and_rotate(im, fine_size):
    from scipy.misc import imresize
    im = np.rot90(im)
    im = imresize(im, (fine_size, fine_size * 2))
    return im

def crop_ratio_2to1(im):
    h, w = im.shape[0], im.shape[1]
    if w > h * 2:
        w_ = h * 2
        margin = int((w - w_) / 2)
        return im[:, margin:w_+1, :]
    else:
        h_ = int(w / 2)
        margin = h - h_
        return im[margin:, :]

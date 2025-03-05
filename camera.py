import numpy as np
import cv2
import logging

def listener(image):
    img = np.array(image.raw_data).reshape((image.height, image.width, 4)) # 4 channels: RGB
    img = img[:, :, :3] # remove alpha channel
    cv2.imshow('image', img) # displays images as they come in
    cv2.waitKey(1)

import cv2
import numpy as np
import sys

def dodgeV2(image, mask):
    return cv2.divide(image, 255-mask, scale=256)

def burnV2(image, mask):
    tmp = np.subtract(255, cv2.divide(255-image, 255-mask, scale=256))
    return tmp

def pencilize():
    pass

def cropWhiteBackgroundToBoundingBox():
    pass

def sketchify(rawImage):
    gray = cv2.cvtColor(rawImage, cv2.COLOR_BGR2GRAY)
    gray_inv = 255 - gray
    blurred = cv2.GaussianBlur(gray_inv, ksize=(21, 21), sigmaX=0, sigmaY=0)
    # blurred = cv2.bilateralFilter(gray_inv, 9, 9, 9)

    blend = dodgeV2(gray, blurred)
    normalized = cv2.normalize(blend, None, 0, 255, cv2.NORM_MINMAX)
    return normalized

if __name__ == "__main__":
    name = sys.argv[1]
    if not name:
        name = "images/beach_ball.png"
    # name = "images/bicycle.png"
    pencilized = sketchify(cv2.imread(name))
    cv2.imshow("pencil sketch", pencilized)
    cv2.waitKey(0)

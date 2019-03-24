import cv2
import numpy as np

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
    
    blend = dodgeV2(gray, blurred)
    return blend

if __name__ == "__main__":
    name = "images/beach_ball.jpeg"
    pencilized = sketchify(cv2.imread(name))
    cv2.imshow("pencil sketch", pencilized)
    cv2.waitKey(0)
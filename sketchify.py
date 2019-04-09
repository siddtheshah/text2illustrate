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
    width, height = rawImage.shape[:2]
    alpha = rawImage[:,:,3]
    gray = cv2.cvtColor(rawImage, cv2.COLOR_BGR2GRAY)
    gray_inv = 255 - gray
    blurred = cv2.GaussianBlur(gray_inv, ksize=(21, 21), sigmaX=0, sigmaY=0)
    # blurred = cv2.bilateralFilter(gray_inv, 9, 9, 9)

    blend = dodgeV2(gray, blurred)
    normalized = cv2.normalize(blend, None, 0, 255, cv2.NORM_MINMAX)
    mask = np.logical_and(alpha > 0, normalized > 100)
    alpha[mask] = 255
    alpha[np.logical_not(mask)] = 0
    rgb = cv2.cvtColor(normalized, cv2.COLOR_GRAY2RGB)
    return (np.stack((rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2], alpha), axis=2), width, height)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "images/ball.png"
    # name = "images/bicycle.png"
    pencilized, width, height = sketchify(cv2.imread(name, cv2.IMREAD_UNCHANGED))
    cv2.imshow("pencil sketch", pencilized[:, :, :3])
    cv2.waitKey(0)

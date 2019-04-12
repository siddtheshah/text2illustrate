import cv2
import numpy as np
import sys
import scipy.ndimage

def dodgeV2(image, mask):
    return cv2.divide(image, 255-mask, scale=256)

def burnV2(image, mask):
    tmp = np.subtract(255, cv2.divide(255-image, 255-mask, scale=256))
    return tmp

def dodge(front,back):
    result=front*255/(255-back + 1)
    result[np.logical_or(result > 255, back ==255)] =255
    return result.astype('uint8')

# takes in np array
def killWaterMarks(image):
    avg = np.sum(image, axis=2)/3
    r = image[:,:, 0]
    b = image[:,:, 1]
    g = image[:,:, 2]
    colorfulness = np.power((np.power(r-avg, 2) + np.power(g-avg, 2) + np.power(b - avg, 2)), .5)
    image[np.logical_and(colorfulness < 5, avg > 150)] = 255
    return image

def cropWhiteBackgroundToBoundingBox():
    pass

# def sketchify(rawImage):
#     width, height = rawImage.shape[:2]
#     alpha = rawImage[:,:,3]
#     gray = cv2.cvtColor(rawImage, cv2.COLOR_BGR2GRAY)

#     gray_inv = 255 - gray
#     blurred = cv2.GaussianBlur(gray_inv, ksize=(21, 21), sigmaX=0, sigmaY=0)
#     # blurred = cv2.bilateralFilter(gray_inv, 9, 9, 9)
#     blend = dodgeV2(gray, blurred)
#     # cv2.imshow("blend", blend)
#     # cv2.waitKey(0)
#     normalized = cv2.normalize(blend, None, 0, 255, cv2.NORM_MINMAX)

#     mask = np.logical_and(alpha > 0, normalized > 0)
#     alpha[mask] = 255
#     alpha[np.logical_not(mask)] = 0
#     rgb = cv2.cvtColor(normalized, cv2.COLOR_GRAY2RGB)
#     return (np.stack((rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2], alpha), axis=2), width, height)


# Takes in an already resized image. DO NOT RESIZE AFTERWARD. You've been warned.
def sketchify(resized):
    # resized = cv2.resize(rawImage, (300, 300))
    width, height = resized.shape[:2]
    alpha = resized[:,:,3]
    marked_img = resized[:,:, :3]

    cleaned_img = killWaterMarks(marked_img)
    # cv2.imshow("blend", cleaned_img)
    # cv2.waitKey(0)

    
    gray_img = np.dot(marked_img[...,:3], [0.299, 0.587, 0.114])
    gray_inv_img = 255-gray_img
    blur_img = scipy.ndimage.filters.gaussian_filter(gray_inv_img,sigma=11)
    blend= dodge(blur_img,gray_img)
    normalized = cv2.normalize(blend, None, 0, 255, cv2.NORM_MINMAX)
    
    normalized[normalized < 240] = 0 # Dump all non dark parts.
    # Now that we have the "core" darkness, we smear it out a bit.
    # elements in the interior of a dark polygon get darker than those outside it.
    reblur = scipy.ndimage.filters.gaussian_filter(normalized,sigma=9)

    # mask = np.logical_and(alpha == 0, reblur > 245)
    alpha[alpha > 0] = 0
    mask = reblur < 250
    alpha[mask] = 255
    
    alphaMap = cv2.cvtColor(alpha, cv2.COLOR_GRAY2RGB)
    cv2.imshow("pencil sketch", alphaMap)
    cv2.waitKey(0)


    rgb = cv2.cvtColor(normalized, cv2.COLOR_GRAY2RGB)
    return np.stack((rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2], alpha), axis=2)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "images/dog0.png"
    print(name)
    # name = "images/bicycle.png"
    pencilized = sketchify(cv2.imread(name, cv2.IMREAD_UNCHANGED))
    cv2.imshow("pencil sketch", pencilized[:, :, :3])
    cv2.waitKey(0)

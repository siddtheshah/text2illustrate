import cv2
import numpy as np
import sys
import scipy.ndimage
# import matplotlib.pyplot as plt

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
    if np.max(colorfulness) > 10: # image is not too gray. Proceed with kill
        image[np.logical_and(colorfulness < 5, avg > 150)] = 255
    return image

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
    blend = dodge(blur_img,gray_img)
    sketch = cv2.normalize(blend, None, 0, 255, cv2.NORM_MINMAX)

    # sketch = np.power(sketch, 2)/ 255
    normalized = np.copy(sketch)

    normalized[normalized < 240] = 0 # Dump all non dark parts.
    # Now that we have the "core" darkness, we smear it out a bit.
    # elements in the interior of a dark polygon get darker than those outside it.
    reblur = scipy.ndimage.filters.gaussian_filter(normalized,sigma=7)

    # mask = np.logical_and(alpha == 0, reblur > 245)
    alpha[alpha > 0] = 0
    mask = reblur < 250
    alpha[mask] = 255
    
    # alphaMap = cv2.cvtColor(alpha, cv2.COLOR_GRAY2RGB)
    # cv2.imshow("pencil sketch", alphaMap)
    # cv2.waitKey(0)

    rgb = cv2.cvtColor(normalized, cv2.COLOR_GRAY2RGB)
    return np.stack((rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2], alpha), axis=2)

def sketchifyCompare(resized):
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
    blend = dodge(blur_img,gray_img)
    sketch = cv2.normalize(blend, None, 0, 255, cv2.NORM_MINMAX)

    # sketch = np.power(sketch, 2)/ 255
    normalized = np.copy(sketch)

    normalized[normalized < 240] = 0 # Dump all non dark parts.
    # Now that we have the "core" darkness, we smear it out a bit.
    # elements in the interior of a dark polygon get darker than those outside it.
    reblur = scipy.ndimage.filters.gaussian_filter(normalized,sigma=7)

    # mask = np.logical_and(alpha == 0, reblur > 245)
    alpha[alpha > 0] = 0
    mask = reblur < 250
    alpha[mask] = 255
    
    fig = plt.figure()
    fig.add_subplot(2, 2, 1)
    plt.imshow(cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))
    fig.add_subplot(2, 2, 2)
    plt.imshow(cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR))
    fig.add_subplot(2, 2, 3)
    plt.imshow(cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR))
    fig.add_subplot(2, 2, 4)
    plt.imshow(cv2.cvtColor(alpha, cv2.COLOR_GRAY2BGR))
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = "images/dog1.png"
    print(name)
    # name = "images/bicycle.png"
    pencilized = sketchify(cv2.imread(name, cv2.IMREAD_UNCHANGED))
    cv2.imshow("pencil sketch", pencilized[:, :, :3])
    cv2.waitKey(0)
    
    #sketchifyCompare(cv2.imread("images/cat0.png", cv2.IMREAD_UNCHANGED))

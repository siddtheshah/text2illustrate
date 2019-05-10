import cv2
import numpy as np
import sys
import scipy.ndimage
import os
import json
import math
# import matplotlib.pyplot as plt

def facingAngle(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    # cv2.imshow("Inv image", thresh)
    # cv2.waitKey()

    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    if not contours:
        return None, None

    cnt = max(contours, key=cv2.contourArea)
    if len(cnt) < 5:
        return None, None
    M = cv2.moments(cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    x = [xy[0][0].tolist() for xy in cnt]
    y = [xy[0][1].tolist() for xy in cnt]
    dx = np.diff(x)
    dy = np.diff(y)
    dx2 = np.diff(dx)
    dy2 = np.diff(dy)

    kmax = 0
    kmin = 10e8
    max_index = None
    min_index = None
    for i in range(len(dx2.tolist())):
        k = (dx[i]*dy2[i] - dy[i]*dx2[i])/(dx[i]**2 + dy[i]**2)**1.5
        # print(k)
        if k > kmax:
            kmax = k
            max_index = i
        if k < kmin:
            kmin = k
            min_index = i

    if max_index:
        index = max_index
    else:
        index = min_index

    # Given a slope of x, y ,the pointing direction is toward y , -x
    # print(index)
    # print(dx[index])

    slopeMag = math.sqrt(dx[index]**2 + dy[index]**2)

    look_x = dy[index]/slopeMag
    look_y = -dx[index]/slopeMag

    return look_x.tolist(), look_y.tolist() 

def boundingBoxAR(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    cv2.imshow("Inv image", thresh)
    cv2.waitKey()

    contours,hierarchy = cv2.findContours(thresh, 1, 2)
    if len(contours) == 0:
        return 1

    cnt = max(contours, key=cv2.contourArea)
    
    # cv2.drawContours(image, contours, -1, (0, 255,0), 3)
    # cv2.imshow('Bounding Box', image)
    # cv2.waitKey()

    x,y,w,h = cv2.boundingRect(cnt)
    # cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0),2)
    # cv2.imshow('Bounding Box', image)
    # cv2.waitKey()
    return h/w

def representativeColor(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    non_white_mask = gray < 250

    pixels = np.float32(image[non_white_mask].reshape(-1, 3))

    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    b, g, r = tuple(palette[np.argmax(counts)])

    return b.tolist(), g.tolist(), r.tolist()

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# Create a json file that contains "name, AR, sin(theta), cos(theta), r, g, b"
def createAnnotations(dirName):
    with open("databaseProcessing/imageIndex.json", 'w+') as outfile:
        data = []
        for file in os.listdir(dirName):
            fileName = dirName + '/' + str(file)
            print(fileName)
            name = str(file)[:-5] # chop off <#>.png

            image = cv2.imread(fileName)
            alphaMinus = image[:, :, :3]

            bounding_box_ar = boundingBoxAR(image)
            b, g, r = representativeColor(image)
            ct, st = facingAngle(image)
            record = {}
            record["path"] = fileName
            record["name"] = name
            record["ar"] = bounding_box_ar
            record["face_x"] = ct
            record["face_y"] = st
            record["color_b"] = b
            record["color_g"] = g
            record["color_r"] = r


            data.append(record)
        json.dump(data, outfile, cls=NumpyEncoder)
            



if __name__ == "__main__":
    if len(sys.argv) > 1:
        dirName = sys.argv[1]
    else:
        dirName = "imagesJPG"

    # createAnnotations(dirName)
    image = cv2.imread(dirName + "/bed0.jpg")
    alphaMinus = image[:, :, :3]
    print(boundingBoxAR(alphaMinus))
    

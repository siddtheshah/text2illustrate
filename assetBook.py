import cv2
import numpy as np
from cv2 import imread
from sketchify import sketchify
from entity import Entity
from pathlib import Path
import collections
import mysql.connector
from mysql.connector import Error

TINY_WIDTH = 50
TINY_HEIGHT = 50

SMALL_WIDTH = 100
SMALL_HEIGHT = 100

MEDIUM_WIDTH = 200
MEDIUM_HEIGHT = 200

LARGE_WIDTH = 300
LARGE_HEIGHT = 300

HUGE_WIDTH = 400
HUGE_HEIGHT = 400
  

class Offset:
    # pos_x,y is a vector from the center of the image, as displayed in TkInter 
    # +x is right, +y is down
    def __init__(self, off_x, off_y, parent):
        self.off_x = off_x
        self.off_y = off_y
        self.parent = parent

    def getXY(self):
        return (self.off_x + self.parent.x, self.off_y + self.parent.y)
 
class EntityImage():
    def __init__(self, cv2_image, width, height, path):
        self.path = path
        # image stuff
        
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.layer = -100
        self.animateFunc = None                # This is a function given by animation object
        self.image = cv2_image
        if self.image is not None:
            self.updateOffsets()

    def updateOffsets(self):
        # Creates 13 offset handles in following formation:
        #              X     X     X
        #                    X  
        #              X  X  X  X  X
        #                    X  
        #              X     X     X

        self.center = Offset(0, 0, self)
        self.center_top = Offset(0, -self.height/4, self)
        self.top = Offset(0, -self.height/2, self)
        self.top_left = Offset(-self.width/2, -self.height/2, self)
        self.top_right = Offset(self.width/2, -self.height/2, self)
        self.left = Offset(-self.width/2, 0, self)
        self.center_left = Offset(-self.width/4, 0, self)
        self.center_right = Offset(self.width/4, 0, self)
        self.right = Offset(self.width/2, 0, self)
        self.center_bot = Offset(0, self.height/4, self)
        self.bot_left = Offset(-self.width/2, self.height/2, self)
        self.bot = Offset(0, self.height/2, self)
        self.bot_right = Offset(self.width/2, self.height/2, self)

    def __repr__(self):
        return '\n<\n\tx: {0}\n\ty: {1}\n\tlayer: {2}\n>'.format(
            self.x, self.y, self.layer)


def queryForSize(entity):
    noun = entity.text
    ne_data = entity.ne_annotation
    if 'type' in ne_data:
        if ne_data['type'] == "PERSON":
            if entity.ne_annotation['gender'] == "FEMALE":
                noun = "woman"
            else:
                noun = "man" # Blame language, not me. 
    """ Connect to MySQL database """
    query = "SELECT entity, realworldsize FROM sizes WHERE entity REGEXP %s"
    regexPattern = "obj.*[-_]" + noun + "-" 
    quantized = [SMALL_WIDTH, SMALL_HEIGHT]

    try:
        conn = mysql.connector.connect(host='localhost',
                                       database='text2illustrate',
                                       user='public',
                                       password='password')

        # if conn.is_connected():
        #     print('Connected to MySQL database')
        cursor = conn.cursor()
        cursor.execute(query, (regexPattern, ))
        rows = cursor.fetchall()

        # for row in rows:
        #     print(row)
        if rows:
            vals = [row[1] for row in rows]
            median = np.median(vals)
        else:
            median = 3
        print(median)
        quantized = sizeQuantizer(median)

        if "small" in entity.adjectives:
            quantized[0]*=.6
            quantized[1]*=.6
        elif "big" in entity.adjectives:
            quantized[0]*=1.5
            quantized[1]*=1.5

 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()
    quantized = [int(q) for q in quantized]
    # print(quantized)
    return tuple(quantized)

def sizeQuantizer(sizeMetric):
    if sizeMetric < 1:
        return [TINY_WIDTH, TINY_HEIGHT]
    elif sizeMetric < 4:
        return [SMALL_WIDTH, SMALL_HEIGHT]
    elif sizeMetric < 15:
        return [MEDIUM_WIDTH, MEDIUM_HEIGHT]
    elif sizeMetric < 100:
        return [LARGE_WIDTH, LARGE_HEIGHT]
    else:
        return [HUGE_WIDTH, HUGE_HEIGHT]

 
class AssetBook:
 
    def __init__(self):
        self.reuse = {}
        self.distinguishCounts = collections.Counter()

 
    def attachImageToEntity(self, entity):
        # reads file from image folder whose name matches Entity.text
        if entity.text in self.reuse:
            pencil_image, width, height, path = self.reuse[entity.text]
            print("Reusing " + entity.text)
        else:
            width, height = queryForSize(entity)
            path, unprocessed = self.getRawImage(entity)
            if unprocessed is not None:
                resized = cv2.resize(unprocessed, (width, height))
                pencil_image = sketchify(resized)
                # cv2.imshow("foo", pencil_image)
                # cv2.waitKey(0)
                self.reuse[entity.text] = (pencil_image, width, height, path)
            else:
                pencil_image = None
                width = 0
                height = 0
                path = ""
        entity.eImage = EntityImage(pencil_image, width, height, path)
        # print(entity.eImage.image.shape[:2])

        # more complex logic for image retrieval

    def getRawImage(self, entity):
    # Here we would make a request to a visual database.
        file_title = entity.text
        result = self.getImageIfThere(file_title) # try something direct
        if result is not None:
            return result
        elif 'type' in entity.ne_annotation: # otherwise redirect
            if entity.ne_annotation['type'] == "PERSON":
                if entity.ne_annotation['gender'] == "FEMALE":
                    file_title = "woman"
                else:
                    file_title = "man" # Blame language, not me.
                return self.getImageIfThere(file_title)
        return None, None

    def getImageIfThere(self, file_title):
        i = self.distinguishCounts[file_title]
        while i < 3:
            file = Path("images/" + file_title + str(i) + ".png")
            print(file)
            if file.is_file():
                try:
                    ret = imread("images/" + file_title + str(i)  + ".png", cv2.IMREAD_UNCHANGED)
                    self.distinguishCounts[file_title] = i + 1
                    return (str(file), ret)
                except:
                    pass
            i += 1
        return None, None

    # Debug method for animate, visualize
    def attachSpecifiedImageToEntity(self, entity, path):
        image = imread(path, cv2.IMREAD_UNCHANGED)
        resized = cv2.resize(image, (SMALL_WIDTH, SMALL_HEIGHT))
        pencil_image = sketchify(resized)
        entity.eImage = EntityImage(pencil_image, SMALL_WIDTH, SMALL_HEIGHT, path)


if __name__ == "__main__":
    # entity = Entity()
    entity = Entity("dog")
    ast = AssetBook()
    ast.attachImageToEntity(entity)

    # SQL query for size tests.
    # entity = Entity("knife")
    # queryForSize(entity)

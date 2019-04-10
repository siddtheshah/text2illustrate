import cv2
import numpy as np
from cv2 import imread
from sketchify import sketchify
import entity
from pathlib import Path
import collections
 
# super lame way to pull images, but setting up a
# visual database is a lot of work when I really need to get a concept
# going here.

# This class 

class Offset:
    # pos_x,y is a vector from the topleft corner of the image. 
    # +x is right, +y is down
    def __init__(self, off_x, off_y, parent):
        self.off_x = off_x
        self.off_y = off_y
        self.parent = parent
 
class EntityImage():
    def __init__(self, cv2_image, width, height):
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
        self.center = Offset(self.width/2, self.height/2, self)
        self.center_top = Offset(self.width/2, self.height/4, self)
        self.top = Offset(self.width/2, 0, self)
        self.top_left = Offset(0, 0, self)
        self.top_right = Offset(self.width, 0, self)
        self.left = Offset(0, self.height/2, self)
        self.center_left = Offset(self.width/4, self.height/2, self)
        self.center_right = Offset(self.width*3/4, self.height/2, self)
        self.right = Offset(self.width, self.height/2, self)
        self.center_bot = Offset(self.width/2, self.height*3/4, self)
        self.bot_left = Offset(0, self.height, self)
        self.bot = Offset(self.width/2, self.height, self)
        self.bot_right = Offset(self.width, self.height, self)

    def __repr__(self):
        return '\n<\n\tx: {0}\n\ty: {1}\n\tlayer: {2}\n>'.format(
            self.x, self.y, self.layer)


 
class AssetBook:
 
    def __init__(self):
        self.reuse = {}
        self.distinguishCounts = collections.Counter()

 
    def attachImageToEntity(self, entity):
        # reads file from image folder whose name matches Entity.text
        if entity.text in self.reuse:
            pencil_image, width, height = self.reuse[entity.text]
            print("Reusing " + entity.text)
        else:
            unprocessed = self.getRawImage(entity)
            if unprocessed is not None:
                pencil_image, width, height = sketchify(unprocessed)
                self.reuse[entity.text] = (pencil_image, width, height)
            else:
                pencil_image = None
                width = 0
                height = 0
        entity.eImage = EntityImage(pencil_image, width, height)
        # print(entity.eImage.image.shape[:2])
        # cv2.imshow("fuck you", entity.eImage.image)
        # cv2.waitKey(0)
        # more complex logic for image retrieval

    def getRawImage(self, entity):
    # Here we would make a request to a visual database.
        while self.distinguishCounts[entity.text] < 3:
            self.distinguishCounts[entity.text] += 1
            file_title = entity.text
            if 'type' in entity.ne_annotation:
                if entity.ne_annotation['type'] == "PERSON":
                    if entity.ne_annotation['gender'] == "FEMALE":
                        file_title = "woman"
                    else:
                        file_title = "man" # Blame language, not me. 
            file = Path("images/" + file_title + str(self.distinguishCounts[entity.text] - 1) + ".png")
            if file.is_file():
                try:
                    ret = imread("images/" + file_title + str(self.distinguishCounts[entity.text] - 1)  + ".png", cv2.IMREAD_UNCHANGED)
                    return ret
                except:
                    continue
            else:
                continue
        return None

# if __name__ == "__main__":
    # entity = Entity()
    # entity.text = "dog"
    # ast = AssetBook()
    # ast.attachImageToEntity(entity)

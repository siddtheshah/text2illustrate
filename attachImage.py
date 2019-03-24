import cv2
import numpy as np
from cv2 import imread
 
# super lame way to pull images, but setting up a
# visual database is a lot of work when I really need to get a concept
# going here.
def getRawImage(entity):
    return imread("images/" + e.text + ".png")
 
class ImageSupplier:
 
    def __init__(self):
        self.reuse = {}
 
    def attachImageToEntity(self, entity):
        # reads file from image folder whose name matches Entity.text
        if entity.text in self.reuse:
            entity.eImage = self.reuse[entity.text]
        else:
            unprocessed = getRawImage(entity)
            pencil_image = sketchify(unprocessed)
            entity.eImage = EntityImage(pencil_image)
            self.reuse[entity.text] = entity.eImage
        # more complex logic for image retrieval

class Offset:
    # pos_x,y is a vector from the topleft corner of the image. 
    # +x is right, +y is down
    def __init__(self, pos_x, pos_y, parent):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.parent = parent
 
class EntityImage:
    def __init__(self, cv2_image):
        self.image = cv2_image
        self.width, self.height = cv2_image.shape[:2]
        self.createOffsets()

    def createOffsets(self):
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

        # Creates 13 offset handles in following formation:
        #              X     X     X
        #                    X  
        #              X  X  X  X  X
        #                    X  
        #              X     X     X
import cv2
import numpy as np
from cv2 import imread
from sketchify import sketchify
 
# super lame way to pull images, but setting up a
# visual database is a lot of work when I really need to get a concept
# going here.
def getRawImage(entity):
    # Here we would make a request to a visual database. 
    return imread("images/" + e.text + ".png")
 
class AssetBook:
 
    def __init__(self):
        self.reuse = {}
 
    def getImageForEntity(self, entity):
        # reads file from image folder whose name matches Entity.text
        if entity.text in self.reuse:
            pencil_image = self.reuse[entity.text]
        else:
            unprocessed = getRawImage(entity)
            pencil_image = sketchify(unprocessed)
            self.reuse[entity.text] = pencil_image
        return pencil_image
        # more complex logic for image retrieval


        
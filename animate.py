

class PathAnimationFunction:

    # This class is capable of creating paths for stuff to follow.
    # 

    def __init__(self, image, action, frameTotal):
        self.frameTotal = frameTotal
        self.startXY = image.shape
        self.endXY = endXY
        self.frameNumber = 0

        # Add the logic
        # if action == "TRANSLATE":
        #     self.updateXY = self.translate
        # elif action ==

    def nextFrame(self):
        if frameNumber < frameTotal:
            self.updateXY()
            frameNumber += 1

    def updateXY(self):
        raise NotImplementedError("PathAnimationFunction is virtual")
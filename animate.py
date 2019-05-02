from entity import Entity
import endpointResolver
import math
from collections import defaultdict
import random

class Animator:
    # for now, we won't split up the frametotal. This means all animations have duration
    # equal to the scene's.
    def assignAnimation(self, entityList, frameTotal):
        i = 0
        while i < len(entityList):
            subj = entityList[i]
            verbDict = defaultdict(list)

            if subj.eImage.image is None:
                subj.eImage.animateFunc = Stationary(subj.eImage, (0, 0), frameTotal)
                continue
            elif subj.eImage.animateFunc is not None:
                continue

            for bv, prep, obj in zip(subj.baseVerbs, subj.preps, subj.objs):
                verbDict[bv].append([prep, obj])
            
            # assign action using this switch statement. 
            # Ordered by priority. Specific stuff first, then general, then stationary
            func = None
            if verbDict["throw"]:
                func = self.animate_throw
            elif verbDict["leap"]:
                func = self.animate_leap
            elif any([verbDict[x] for x in endpointResolver.MOTION_OTHER]):
                func = self.animate_attach_go
            elif any([verbDict[x] for x in endpointResolver.MOTION_SELF]):
                func = self.animate_go
            elif any([verbDict[x] for x in endpointResolver.SPEAK]):
                func = self.animate_speak
            else:
                func = self.animate_stationary
            func(subj, verbDict, frameTotal)
            i += 1

    def animate_throw(self, subj, verbDict, frameTotal):
        throwPairs = verbDict["throw"]
        for prep, obj in throwPairs:
            if prep:
                endOffset = obj.eImage.center
            else:
                startOffset = obj.eImage.center
        obj.eImage.animateFunc = Align(startOffset, endOffset, frameTotal)

    def animate_leap(self, subj, verbDict, frameTotal):
        prep, obj = verbDict["leap"][0]
        startXY = (subj.eImage.x, subj.eImage.y)
        pivotXY = (obj.eImage.x, obj.eImage.y)
        if prep in ["to", "after", "toward", "near", "at"]:
            subj.eImage.animateFunc = JumpToward(subj.eImage.center, obj.eImage.center, frameTotal)
        else:
            subj.eImage.animateFunc = JumpOver(subj.eImage.center, obj.eImage.center, frameTotal)

    def animate_attach_go(self, subj, verbDict, frameTotal):
        goPairs = []
        for verb in endpointResolver.MOTION_OTHER:
            goPairs.extend(verbDict[verb])
        endOffset = None
        attached = None
        for prep, obj in goPairs:
            if prep:
                end = obj
            else:
                attached = obj.eImage
        if endOffset:
            subj.eImage.animateFunc = GoOmniAlign(subj.eImage, end.eImage, frameTotal)
        if attached:
            attached.animateFunc = AttachedMotion(attached, attached.center, subj.eImage.center_right, frameTotal)

    def animate_go(self, subj, verbDict, frameTotal):
        goPairs = []
        for verb in endpointResolver.MOTION_SELF:
            goPairs.extend(verbDict[verb])
        prep, obj = goPairs[0]
        subj.eImage.animateFunc = GoOmniAlign(subj.eImage, obj.eImage, frameTotal)

    def animate_speak(self, subj, verbDict, frameTotal):
        speakPairs = []
        for verb in endpointResolver.SPEAK:
            speakPairs.extend(verbDict[verb])
        prep, obj = goPairs[0]
        subj.eImage.animateFunc = Jiggle(subj.eImage, frameTotal)

    def animate_stationary(self, subj, verbDict, frameTotal):
        subj.eImage.animateFunc = Stationary(subj.eImage, frameTotal)



class Trajectory:
    def __init__(self, eImage, startXY, frameTotal):
        self.eImage = eImage
        self.startXY = startXY
        self.frameTotal = frameTotal
        self.frameNumber = 0
        self.xt = self.startXY[0]
        self.yt = self.startXY[1]
        self.ut = 1                # Visibility enable, defaulted to visible
        self.xt_old = self.startXY[0]
        self.yt_old = self.startXY[1]

    def __next__(self):
        self.xt_old, self.yt_old = self.xt, self.yt
        return self.next()
         

    def getDelta(self):
        return (self.xt - self.xt_old, self.yt - self.yt_old, self.ut)

    def eager(self):
        self.frameNumber = 0
        ret = []
        while self.frameNumber < self.frameTotal:
            ret.append(self.next())
            self.frameNumber += 1
        return ret

    def next(self):
        pass

# Special tools

class AttachedMotion(Trajectory):
    def __init__(self, heldOffset, holderOffset, frameTotal):
        super().__init__(self, heldOffset.parent, holderOffset.getXY(), holderOffset.getXY(), frameTotal)
        self.parent = holderOffset.parent

    def next(self):
        self.frameNumber += 1
        self.xt = self.parent.animateFunc.xt + holderOffset.off_x - heldOffset.off_x
        self.yt = self.parent.animateFunc.yt + holderOffset.off_y - heldOffset.off_y
        self.ut = self.parent.animateFunc.ut
        return self.xt, self.yt, self.ut

class Delay(Trajectory):
    def __init__(self, eImage, startXY, frameTotal, trajectory):
        super().__init__(eImage, startXY, frameTotal)
        self.trajectory = trajectory

    def next(self):
        self.frameNumber += 1
        if self.frameNumber < self.frameTotal:
            return int(self.xt), int(self.yt), self.ut
        else:
            self.xt, self.yt, self.ut = next(self.trajectory)
            return self.xt, self.yt, self.ut

class Stationary(Trajectory):
    def __init__(self, eImage, frameTotal):
        startXY = (eImage.x, eImage.y)
        super().__init__(eImage, startXY, frameTotal)

    def next(self):
        self.frameNumber += 1
        return int(self.xt), int(self.yt), self.ut

# Basic linear movements

class TranslateLinear(Trajectory):
    def __init__(self, eImage, startXY, endXY, frameTotal):
        super().__init__(eImage, startXY, frameTotal)
        self.endXY = endXY

    def next(self):
        self.frameNumber += 1
        x0, y0 = self.startXY
        x1, y1 = self.endXY
        self.xt = x0 + (x1 - x0)*self.frameNumber/self.frameTotal
        self.yt = y0 + (y1 - y0)*self.frameNumber/self.frameTotal
        return int(self.xt), int(self.yt), self.ut

class Align(TranslateLinear):
    def __init__(self, subjOffset, objOffset, frameTotal):
        eImage = subjOffset.parent
        startXY = (eImage.x, eImage.y)
        endX = objOffset.off_x - subjOffset.off_x + objOffset.parent.x
        endY = objOffset.off_y - subjOffset.off_y + objOffset.parent.y
        endXY = (endX, endY)
        super().__init__(eImage, startXY, endXY, frameTotal)

class GoOmniAlign(Align):
    def __init__(self, eImageGo, eImageDest, frameTotal):
        verticality = (eImageGo.y - eImageDest.y)/(eImageGo.x - eImageDest.x -.5)
        if verticality > 1 or verticality < -1:
            if eImageGo.y < eImageDest.y:
                super().__init__(eImageGo.center_top, eImageDest.center_bot, frameTotal)
            elif eImageGo.y > eImageDest.y:
                super().__init__(eImageGo.center_bot, eImageDest.center_top, frameTotal)
        else:
            if eImageGo.x < eImageDest.x:
                super().__init__(eImageGo.center_right, eImageDest.center_left, frameTotal)
            elif eImageGo.x > eImageDest.x:
                super().__init__(eImageGo.center_left, eImageDest.center_right, frameTotal)


# Jumping animations

class PivotOverhand(Trajectory):
    def __init__(self, eImage, startXY, pivotXY, frameTotal):
        super().__init__(eImage, startXY, frameTotal)
        self.pivotXY = pivotXY

    def next(self):
        self.frameNumber += 1
        x0, y0 = self.startXY
        x1, y1 = self.pivotXY
        if x0 < x1:
            direction = -1
        else:
            direction = 1
        r = math.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        self.xt = x1 + r*direction*math.cos(self.frameNumber/self.frameTotal*math.pi)
        self.yt = y1 - r*math.sin(self.frameNumber/self.frameTotal*math.pi)
        return int(self.xt), int(self.yt), self.ut

class JumpToward(PivotOverhand):
    def __init__(self, subjOffset, objOffset, frameTotal):
        startXY = subjOffset.getXY()
        endXY = objOffset.getXY()
        pivotXY = (startXY[0]/2 + endXY[0]/2, startXY[1]/2 + endXY[1]/2)
        super().__init__(subjOffset.parent, startXY, pivotXY, frameTotal)

class JumpOver(PivotOverhand):
    def __init__(self, subjOffset, objOffset, frameTotal):
        startXY = subjOffset.getXY()
        pivotXY = objOffset.getXY()
        super().__init__(subjOffset.parent, startXY, pivotXY, frameTotal)

# Speaking animation. Basically just a jiggle.

class Jiggle(Trajectory):
    def __init__(self, eImage, frameTotal):
        startXY = (eImage.x, eImage.y)
        super().__init__(eImage, startXY, frameTotal)

    def next(self):
        phaseRandomizationX = random.uniform(0, self.frameTotal)
        phaseRandomizationY = random.uniform(0, self.frameTotal)
        x0, y0 = self.startXY
        self.xt = x0 + 10*math.sin(2*(self.frameNumber + phaseRandomizationX)/self.frameTotal*math.pi)
        self.yt = y0 + 50*math.sin(2*(self.frameNumber + phaseRandomizationY)/self.frameTotal*math.pi)
        return int(self.xt), int(self.yt), self.ut




if __name__ == "__main__":
    import tkinter as tk
    from tkinter import *
    from assetBook import AssetBook
    from PIL import Image, ImageTk
    import cv2
    ast = AssetBook()

    dog = Entity("dog")
    dog.baseVerbs.append("leap")
    dog.preps.append("to")
    
    store = Entity("store")
    dog.objs.append(store)

    ast.attachSpecifiedImageToEntity(dog, cv2.imread("images/dog0.png", cv2.IMREAD_UNCHANGED))
    ast.attachSpecifiedImageToEntity(store, cv2.imread("images/store0.png", cv2.IMREAD_UNCHANGED))

    dog.eImage.x = 0
    dog.eImage.y = 400

    store.eImage.x = 400
    store.eImage.y = 400

    entityList = [dog, store]

    Animator().assignAnimation(entityList, 10000)

    class GUI(tk.Tk):
        def __init__(self):
            tk.Tk.__init__(self)
            self.canvas = Canvas(self, width=800, height=600, bg="white")
            self.canvas.pack()
            self.frameCounter = 0
            self.frameLimit = 10000
            self.imageMap = {}
            self.images = []

        def addEntities(self, entityList):
            for entity in entityList:
                im = Image.fromarray(entity.eImage.image)
                imgtk = ImageTk.PhotoImage(image=im.convert("RGBA"))
                objOnCanvas = self.canvas.create_image((entity.eImage.x, entity.eImage.y), image=imgtk)
                self.imageMap[entity.text] = objOnCanvas
                self.images.append(imgtk)

            print("Drawn")
            self.after(0, self.playAnimation)

        def playAnimation(self):
            while self.frameCounter < self.frameLimit:
                # print(self.frameCounter)
                for entity in entityList:
                    # print(entity)
                    animation = entity.eImage.animateFunc
                    if animation:
                        next(animation)
                        delta = animation.getDelta()
                        if delta[2] == 1:
                            self.canvas.move(self.imageMap[entity.text], delta[0], delta[1])
                #if self.frameCounter % 50 == 0:
                self.canvas.update()
                self.frameCounter += 1

    gui = GUI()
    gui.addEntities(entityList)
    gui.mainloop()




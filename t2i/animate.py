from t2i.entity import Entity
import t2i.endpointResolver as endpointResolver
import math
from collections import defaultdict
import random

class Animator:
    # for now, we won't split up the frametotal. This means all animations have duration
    # equal to the scene's.
    def assignAnimations(self, entityList, frameTotal):
        i = 0
        backMap = {}
        for entity in entityList:
            backMap[entity.text] = entity

        while i < len(entityList):
            subj = entityList[i]
            verbDict = defaultdict(list)

            if subj.eImage.image is None:
                subj.eImage.animateFunc = Stationary(subj.eImage, frameTotal)
                i += 1
                continue
            elif subj.eImage.animateFunc is not None:
                i += 1
                continue

            for bv, prep, obj in zip(subj.baseVerbs, subj.preps, subj.objs):
                obj = backMap[obj.text] # 
                verbDict[bv].append([prep, obj])
            # print(verbDict)
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

        for entity in entityList:
            if not entity.eImage.animateFunc:
                entity.eImage.animateFunc = Stationary(entity.eImage, frameTotal)


    def animate_throw(self, subj, verbDict, frameTotal):
        print("Animate throw triggered: " + subj.text)
        throwPairs = verbDict["throw"]
        endOffset = None
        prep = None
        thrown  = None
        for prep, obj in throwPairs:
            if prep:
                endOffset = obj.eImage.center
            else:
                startOffset = obj.eImage.center
                thrown = obj
        if not endOffset or not thrown:
            thrown.eImage.animateFunc = Stationary(obj.eImage, frameTotal)
            return
        thrown.eImage.animateFunc = Align(startOffset, endOffset, frameTotal)

    def animate_leap(self, subj, verbDict, frameTotal):
        print("Animate leap triggered: " + subj.text)
        prep, obj = verbDict["leap"][0]
        startXY = (subj.eImage.x, subj.eImage.y)
        pivotXY = (obj.eImage.x, obj.eImage.y)
        if prep in ["to", "after", "toward", "near", "at"]:
            subj.eImage.animateFunc = JumpToward(subj.eImage.center, obj.eImage.center, frameTotal)
        else:
            subj.eImage.animateFunc = JumpOver(subj.eImage.center, obj.eImage.center, frameTotal)

    def animate_attach_go(self, subj, verbDict, frameTotal):
        print("Animate attach_go triggered: " + subj.text)
        goPairs = []
        for verb in endpointResolver.MOTION_OTHER:
            goPairs.extend(verbDict[verb])
        end = None
        attached = None
        for prep, obj in goPairs:
            if prep:
                end = obj
            else:
                attached = obj.eImage
        if end:
            print(end)
            subj.eImage.animateFunc = GoOmniAlign(subj.eImage, end.eImage, frameTotal)
        if attached:
            attached.animateFunc = AttachedMotion(attached.center, subj.eImage.center_right, frameTotal)

    def animate_go(self, subj, verbDict, frameTotal):
        print("Animate go triggered: " + subj.text)
        goPairs = []
        for verb in endpointResolver.MOTION_SELF:
            goPairs.extend(verbDict[verb])
        while len(goPairs) > 0:
            prep, obj = goPairs.pop(0)
            if obj.eImage.image is not None:
                subj.eImage.animateFunc = GoOmniAlign(subj.eImage, obj.eImage, frameTotal)
                return

    def animate_speak(self, subj, verbDict, frameTotal):
        print("Animate speak triggered: " + subj.text)
        speakPairs = []
        for verb in endpointResolver.SPEAK:
            speakPairs.extend(verbDict[verb])
        prep, obj = speakPairs[0]
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
            ret.append(list(self.next()))
            self.frameNumber += 1
        return ret

    def next(self):
        pass

# Special tools

class AttachedMotion(Trajectory):
    def __init__(self, heldOffset, holderOffset, frameTotal):
        self.heldOffset = heldOffset
        self.holderOffset = holderOffset
        self.parent = holderOffset.parent
        super().__init__(heldOffset.parent, (heldOffset.parent.x, heldOffset.parent.y), frameTotal)

    def next(self):
        self.frameNumber += 1
        self.xt = self.parent.animateFunc.xt + self.holderOffset.off_x - self.heldOffset.off_x
        self.yt = self.parent.animateFunc.yt + self.holderOffset.off_y - self.heldOffset.off_y
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
        self.xt = x0 + 10*math.sin((self.frameNumber + phaseRandomizationX)/self.frameTotal*math.pi/2)
        self.yt = y0 + 30*math.sin((self.frameNumber + phaseRandomizationY)/self.frameTotal*math.pi/2)
        self.frameNumber += 1
        return int(self.xt), int(self.yt), self.ut




if __name__ == "__main__":
    import tkinter as tk
    from tkinter import *
    from assetBook import AssetBook
    from PIL import Image, ImageTk
    import cv2
    ast = AssetBook()

    subj = Entity("man")
    subj.baseVerbs.append("run")
    subj.preps.append("")
    
    obj = Entity("dog")
    subj.objs.append(obj)

    ast.attachSpecifiedImageToEntity(subj, "images/dog0.png")
    ast.attachSpecifiedImageToEntity(obj, "images/store0.png")

    subj.eImage.x = 0
    subj.eImage.y = 400

    obj.eImage.x = 400
    obj.eImage.y = 400

    entityList = [subj, obj]

    Animator().assignAnimations(entityList, 10000)

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




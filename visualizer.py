import cv2
import numpy as np

from entity import *
from script import *
from assetBook import *
from endpointResolver import *
import animate
from threading import Lock, Thread

CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 800

TINY_WIDTH = 100
TINY_HEIGHT = 400

SMALL_WIDTH = 200
SMALL_HEIGHT = 200

MEDIUM_WIDTH = 400
MEDIUM_HEIGHT = 400

LARGE_WIDTH = 550
LARGE_HEIGHT = 550

HUGE_WIDTH = 700
HUGE_HEIGHT = 700

def AlignTo(Offset1, Offset2):
    Offset1.parent.x = Offset2.pos_x - Offset1.pos_x
    Offset1.parent.y = Offset2.pos_y - Offset2.pos_y

class StaticVisualGraph:
    class VisualNode:
        def __init__(self, entity):
            self.entity = entity
            self.isRoot = True
            self.rootOffset = None # Define offsets to be vectors to CENTER of image
            self.otherOffsets = {}
            self.reverse = []
            self.onIsland = False

    class Island:
        def __init__(self, root):
            self.root = root
            self.leftExtent = 0
            self.rightExtent = 0
            self.upExtent = 0
            self.downExtent = 0
            self.nodes = []
            if root.entity.eImage.image is not None:
                self.leftExtent = -root.entity.eImage.width/2
                self.rightExtent = root.entity.eImage.width/2
                self.upExtent =    root.entity.eImage.height/2
                self.downExtent =  -root.entity.eImage.height/2

        def getDimensions(self):
            return (self.rightExtent - self.leftExtent, self.upExtent - self.downExtent)

        def __repr__(self):
            return '\n<\n\tisland: {0}\n\tleft: {1}\n\tright: {2}\n\tup: {3}\n\tdown: {4}\n>'.format(
            self.root.entity, self.leftExtent, self.rightExtent, self.upExtent, self.downExtent)

    def __init__(self, entities):
        # Demotes other entities if they are not roots.
        # If what was once a root was demoted, it is instead no longer a root
        # and the subject gets promoted instead.
        self.map = {}
        for entity in entities:
            self.map[entity.text] = self.VisualNode(entity)
            print(entity)
        for entity in entities:
            forwards = [self.map[obj.text] for obj in entity.objs]
            self.map[entity.text].forward = forwards
        self.nodeList = self.map.values()
        self.islands = []

    def AssignLocations(self):
        self.GetForwardRootsAndReverse()
        self.NodeToNodeOffsets()
        self.CreateIslands()
        self.ArrangeIslands()

    def GetForwardRootsAndReverse(self):
        for node in self.nodeList:
            for child in node.forward:
                child.isRoot = False
                child.reverse.append(node)
        self.roots = list(filter(lambda x: x.isRoot, self.nodeList))

    def NodeToNodeOffsets(self):
        for node in self.nodeList:
            for verb, prep, otherNode in zip(node.entity.baseVerbs, node.entity.preps, node.forward):
                offset = self.SelectOffset(verb, prep)
                if not (node.entity.eImage.image is not None and otherNode.entity.eImage.image is not None):
                    offset*= SMALL_WIDTH
                else:
                    offset*= (node.entity.eImage.width + otherNode.entity.eImage.width)/2
                if offset[2] > 0: 
                    offset[2] = 1
                elif offset[2] < 0:
                    offset[2] = -1         
                node.otherOffsets[otherNode] = offset
                otherNode.otherOffsets[node] = -1*offset #graph is now bidirectional

    def SelectOffset(self, verb, prep):
        offset = np.array([0.5, 0.0, 0.0])
        if prep:
            # Things look inverted because we want the object's relation to us.
            if prep in ["below", "beneath", "under"]: # object is above us, etc
                offset = np.array([0.0, .25, 1.0])
            elif prep in ["with", "to", "at", "before"]: # we're at object. push it back a layer
                offset = np.array([.25, 0.0, -1.0])
            elif prep in ["in", "inside", "into", "within"]: # object in foreground
                offset = np.array([0.0, 0.0, 1.0])
            elif prep in ["beside", "near", "outside"]: # object nearby, we're more important
                offset = np.array([.25, 0.0, -1.0]) 
            elif prep in ["over", "above", "atop", "on", "onto", "upon"]: # object beneath us
                offset = np.array([0.0, -.25, -1.0])
            else:
                offset = np.array([1.0, 0.0, 1.0]) # idk
        return offset

    def CreateIslands(self):
        nodesResolved = 0
        while len(self.roots) > 0 and nodesResolved < len(self.nodeList):
            root = self.roots.pop(0)
            if root.onIsland:
                continue
            else:
                island = self.Island(root)
                root.rootOffset = np.array([0, 0, 0])
                self.islands.append(island)
                toExplore = set([root])
                visited = set()
                # print("New Island")
                # Big diamonds are extremely unusual, so we won't worry about it.
                while toExplore:
                    current = toExplore.pop()
                    # print("Current: " + current.entity.text)
                    current.onIsland = True
                    island.nodes.append(current)
                    nodesResolved += 1
                    if current not in visited:
                        visited.add(current)
                        for other in current.otherOffsets:
                            if other not in visited:
                                # handles depth 1 diamonds
                                offset = current.otherOffsets[other] + current.rootOffset

                                if not other.rootOffset:
                                    other.rootOffset = offset
                                elif SumSq(other.rootOffset) > SumSq(offset):
                                    other.rootOffset = offset 
                                # print("Other: " + other.entity.text)
                                # print(other.rootOffset)
                                if offset[0] < island.leftExtent:
                                    island.leftExtent = offset[0]
                                elif offset[0] > island.rightExtent:
                                    island.rightExtent = offset[0]

                                if offset[1] < island.downExtent:
                                    island.downExtent = offset[1]
                                elif offset[1] > island.upExtent:
                                    island.upExtent = offset[1] 
                                toExplore.add(other)

    def HorizontalBounce(self):
        pass

    def ArrangeIslands(self):
        # Naive pack horizontally
        white_width = CANVAS_WIDTH - sum([island.getDimensions()[0] for island in self.islands])
        width_margin = white_width/(len(self.islands) + 1)
        #filled_width = width_margin + sum([width_margin + island.getDimensions()[0] for island in self.islands])
        # horizontal_unit = CANVAS_WIDTH/filled_width
        # white_height = CANVAS_HEIGHT - max([island.getDimensions()[1] for island in self.islands])
        # height_margin = white_height/(len(self.islands) + 1) 
        # vertical_unit = CANVAS_HEIGHT/filled_height
        
        grid_col = 0
        root_row = 2*CANVAS_HEIGHT/3 
        for island in self.islands:
            grid_col += width_margin
            root_col = grid_col - island.leftExtent
            for node in island.nodes:
                if node.entity.eImage.image is not None:
                    node.entity.eImage.x = (root_col + node.rootOffset[0])
                    node.entity.eImage.y = (root_row - node.rootOffset[1])
                    node.entity.eImage.layer = node.rootOffset[2]
            grid_col += island.getDimensions()[0]
        print("================ ARRANGED ISLANDS =====================")
        print(self.islands)



    def SumSq(offset):
        # This function favors denser packing, if possible.
        return sum(x**2 for x in offset)

class Visualizer:
    def __init__(self, width=CANVAS_WIDTH, height=CANVAS_HEIGHT):
        self.width = width
        self.height = height
        self.assetBook = AssetBook()
        self.script = Script()
        self.visualScript = []        
        # self.lock_ = Lock()


    def DrawStoryWithCallback(self, textBody, callBackFunc):
        self.GetAssets(textBody)
        self.StreamScenes(callBackFunc)
        print("Finished stream")
        self.visualScript = []
        self.script = Script()

    def GetAssets(self, textBody):
        self.script.processEntities(textBody)
        self.script.ResolveAdjectives()
        self.script.CreateContinuum()
        print("============== VISUALIZER ==============")
        self.visualScript = self.script.continuum
        for entityList in self.visualScript:
            for entity in entityList:
                self.assetBook.attachImageToEntity(entity)
                if entity.eImage.image is None:                    
                    print("Could not find image for entity: " + entity.text)

    def StreamScenes(self, callBackFunc):
        # self.lock_.acquire()
        for entityList in self.visualScript:
            self.ArrangeStaticScene(entityList)
            print(entityList)
            # self.ArrangeDynamicScene(entityList)

            callBackFunc(entityList) # Should add in asynchronous processing here

        # self.lock_.release()

    def SetDefaultSizes(self, entitiesWithImage):
        # Here we're going to use some awful logic to determine default size.
        # Replace with look up on Vignet data.
        for entityWithImage in entitiesWithImage:
            if entityWithImage.eImage.image is not None:
                cv2_image = entityWithImage.eImage.image

                resize_width = SMALL_WIDTH
                resize_height = SMALL_HEIGHT
                ne_data = entityWithImage.ne_annotation
                entity_type = None
                if 'type' in ne_data:
                    entity_type = ne_data['type']

                if entity_type:
                    if entity_type == "PERSON":
                        resize_width = MEDIUM_HEIGHT
                        resize_height = MEDIUM_HEIGHT

                if "small" in entityWithImage.adjectives:
                    resize_width*=.75
                    resize_height*=.75
                elif "big" in entityWithImage.adjectives:
                    resize_width*=1.25
                    resize_height*=1.25
                
                resized = cv2.resize(cv2_image, (resize_width, resize_width))
                entityWithImage.eImage = EntityImage(resized, resize_width, resize_height)
        return entitiesWithImage

    def ArrangeStaticScene(self, entityList):
        self.SetDefaultSizes(entityList)
        graph = StaticVisualGraph(entityList)
        graph.AssignLocations()
        return entityList

        # Set default sizes and positions of 


    def ArrangeDynamicScene(self, imageEntities):
        # Creates animation objects from animate.py, uses them to parameterize functions
        # which are then attached to the imageEntities
        pass

def staticShow(entity):
    print("Entity: " + entity.text)
    if entity.eImage.image is None:
        print("Not Found")
    else:
        print(entity.eImage)

def staticShowMultiple(entityList):
    for entity in entityList:
        staticShow(entity)

if __name__ == "__main__":
    v = Visualizer()
    textBody = ("There was a box, a ball, a dog, and a cat.")
    v.DrawStoryWithCallback(textBody, staticShowMultiple)
    # textBody = "The cat sat near the man."
    # v.DrawStoryWithCallback(textBody, staticShowMultiple)


import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from t2i.color import *

import sys


# Verb Endpoints
MOTION_SELF = ["run", "walk", "leap", "go", "move"]
MOTION_OTHER = ["push", "pull", "carry", "throw"]
STATIONARY = ["rest", "sit", "stand"]
SPEAK = ["say", "scream", "whisper"]
USAGE = ["use", "made", "destroy", "have"]
REGARD = ["examine", "see"]
BEING = ["is", "seem", "name"]

# Adjective Endpoints
SIZE = ["small", "big", "wide", "thin", "short", "long"]
COLOR = ["light", "dark", "colorful"] + list(CNAMES.keys())
AGE = ["young", "old"]
EMOTION = ["happy", "sad", "angry", "scared", "thoughtful"]
VOLUME = ["loud", "quiet"]
QUALITY = ["great", "terrible"]
SPEED = ["slow", "fast"]
TEXTURE = ["smooth", "sharp", "straight"]
RIGHTEOUSNESS = ["benevolent", "evil"]

class EndpointResolver:

    def __init__(self, pos, endpoints):
        self.lemmatizer = WordNetLemmatizer()
        self.pos = pos
        self.endpoints = [self.lemmatizer.lemmatize(end) for end in endpoints]

    def resolveWordToEndpointsBFS(self, word, limit=100):
        # Brute force search over synonym graph. 

        endpointSet = set(self.endpoints)
        lemCurrent = self.lemmatizer.lemmatize(word.split("_")[0])
        if lemCurrent in endpointSet:
            return lemCurrent

        seen = set()
        toExplore = [word]
        nextLevel = []
        nextLevelSet = set()
        exploreCount = 0
        
        while exploreCount < limit and len(toExplore) > 0:
            current = toExplore.pop(0)
            if current not in seen:
                seen.add(current)
                current = self.lemmatizer.lemmatize(current)
                # print(current)
                lemCurrent = current.split("_")[0]
                if lemCurrent in endpointSet:
                    return lemCurrent
                syns = wn.synsets(current)
                trimmedByPOS = list(filter(lambda x: x.pos() in self.pos, syns))
                synLems = [l.name() for s in trimmedByPOS for l in s.lemmas()]
                print("Current:", current, ":", synLems)
                # unseen = set(filter(lambda x: x not in seen, synLems))
                unseenList = list(filter(lambda x: x not in seen, synLems))[:7]
                unseen = set(unseenList)
                nextLevel += unseenList
                nextLevelSet |= unseen
                #  print("Current:", current, ":", unseenList)
            if len(toExplore) == 0:
                toExplore = nextLevel
                nextLevelSet = set()
                nextLevel = []
            exploreCount += 1

        return None

    def resolveWordToEndpointsLCH(self, word):
        word = self.lemmatizer.lemmatize(word)
        print(word)
        syns = wn.synsets(word)
        trimmedByPOS = list(filter(lambda x: x.pos() in self.pos, syns))
        max_sim = 0
        best_match = None
        for end in self.endpoints:
            if word == end:
                return end
            endSyns = wn.synsets(end)
            endTrimmed = list(filter(lambda x: x.pos() in self.pos, endSyns))
            for et in endTrimmed:
                for baseSyn in trimmedByPOS:
                    if baseSyn.pos() == et.pos():
                        similarity = baseSyn.lch_similarity(et)
                        if similarity > max_sim:
                            max_sim = similarity
                            best_match = end
        return best_match

    def resolveWordToEndpointsWUP(self, word):
        syns = wn.synsets(word)
        trimmedByPOS = list(filter(lambda x: x.pos() in self.pos, syns))
        max_sim = 0
        best_match = None
        for end in self.endpoints:
            endSyns = wn.synsets(end)
            endTrimmed = list(filter(lambda x: x.pos() in self.pos, endSyns))
            for et in endTrimmed:
                for baseSyn in trimmedByPOS:
                    similarity = baseSyn.wup_similarity(et)
                    if similarity > max_sim:
                        max_sim = similarity
                        best_match = end
        return best_match

class VerbResolver(EndpointResolver):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.pos = ['v']
        endpoints = MOTION_SELF + MOTION_OTHER + STATIONARY + SPEAK + REGARD + BEING + USAGE
        self.endpoints = [self.lemmatizer.lemmatize(end) for end in endpoints]

    def resolve(self, word):
        return self.resolveWordToEndpointsLCH(word)

class AdjectiveResolver(EndpointResolver):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.pos = ['a','s']
        
        endpoints = SIZE + COLOR + AGE + EMOTION + VOLUME + QUALITY + SPEED + TEXTURE + RIGHTEOUSNESS
        self.endpoints = [self.lemmatizer.lemmatize(end) for end in endpoints]

    def resolve(self, word):
        return self.resolveWordToEndpointsBFS(word)

if __name__ == "__main__":
    resolver = VerbResolver()
    if len(sys.argv) > 1:
        testWord = sys.argv[1]
    else:
        testWord = "fell"

    result1 = resolver.resolveWordToEndpointsBFS(testWord, 100)
    if result1:
        print("BFS: " + result1)

    result2 = resolver.resolveWordToEndpointsLCH(testWord)
    if result2:
        print("LCH: " + result2)
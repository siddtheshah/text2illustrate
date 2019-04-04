
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

class EndpointResolver:

    def __init__(self, pos, endpoints):
        self.lemmatizer = WordNetLemmatizer()
        self.pos = pos
        self.endpoints = [self.lemmatizer.lemmatize(end) for end in endpoints]

    def resolveWordToEndpointsBFS(self, word, limit=100):
        # Brute force search over synonym graph. 
        seen = set()
        toExplore = [word]
        nextLevel = []
        nextLevelSet = set()
        endpointSet = set(self.endpoints)
        exploreCount = 0

        while exploreCount < limit and len(toExplore) > 0:
            current = toExplore.pop(0)
            if current not in seen:
                seen.add(current)
                current = self.lemmatizer.lemmatize(current)
                # print(current)
                if current in endpointSet:
                    return current
                syns = wn.synsets(current)
                trimmedByPOS = list(filter(lambda x: x.pos() in self.pos, syns))
                synLems = [l.name() for s in trimmedByPOS for l in s.lemmas()]
                print("Current:", current, ":", synLems)
                unseen = set(filter(lambda x: x not in seen, synLems))
                unseenList = list(filter(lambda x: x not in seen, synLems))
                nextLevelSet |= unseen
                nextLevel += unseenList
                #  print("Current:", current, ":", unseenList)
            if len(toExplore) == 0:
                toExplore = nextLevel
                nextLevelSet = set()
                nextLevel = []
            exploreCount += 1

        return None

    def resolveWordToEndpointsLCH(self, word):
        syns = wn.synsets(word)
        trimmedByPOS = list(filter(lambda x: x.pos() == self.pos, syns))
        max_sim = 0
        best_match = None
        for end in self.endpoints:
            endSyns = wn.synsets(end)
            endTrimmed = list(filter(lambda x: x.pos() == self.pos, endSyns))
            for et in endTrimmed:
                for baseSyn in trimmedByPOS:
                    similarity = baseSyn.lch_similarity(et)
                    if similarity > max_sim:
                        max_sim = similarity
                        best_match = end
        return best_match

    def resolveWordToEndpointsWUP(self, word):
        syns = wn.synsets(word)
        trimmedByPOS = list(filter(lambda x: x.pos() == self.pos, syns))
        max_sim = 0
        best_match = None
        for end in self.endpoints:
            endSyns = wn.synsets(end)
            endTrimmed = list(filter(lambda x: x.pos() == self.pos, endSyns))
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
        motion_self = ["run", "walk", "jump"]
        motion_other = ["throw", "push", "pull", "carry"]
        stationary = ["rest", "sit", "stand"]
        speak = ["say", "scream", "whisper"]
        usage = ["use"]
        regard = ["examine", "look", "see"]
        being = ["is"]
        endpoints = motion_self + motion_other + stationary + speak + regard + being
        self.endpoints = [self.lemmatizer.lemmatize(end) for end in endpoints]

    def resolve(word):
        return self.resolveWordToEndpointsLCH(word)

class AdjectiveResolver(EndpointResolver):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.pos = ['a','s']
        size = ["small", "big", "wide", "thin", "short"]
        color = ["light", "dark", "colorful"]
        age = ["young", "old"]
        emotion = ["happy", "sad", "angry", "scared", "thoughtful"]
        volume = ["loud", "quiet"]
        quality = ["great", "terrible"]
        speed = ["slow", "fast"]
        texture = ["smooth", "sharp", "straight"]
        righteousness = ["benevolent", "evil"]
        endpoints = size + color + age + emotion + volume + quality + speed + texture + righteousness
        self.endpoints = [self.lemmatizer.lemmatize(end) for end in endpoints]

    def resolve(word):
        return self.resolveWordToEndpointsWUP(word)

if __name__ == "__main__":
    resolver = AdjectiveResolver()
    testWord = "grand"

    result1 = resolver.resolveWordToEndpointsBFS(testWord, 100)
    if result1:
        print("BFS: " + result1)

    result2 = resolver.resolveWordToEndpointsWUP(testWord)
    if result2:
        print("WUP: " + result2)
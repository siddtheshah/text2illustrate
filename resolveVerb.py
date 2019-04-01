
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

class EndpointResolver:

    def __init__(self, pos, endpoints):
        self.lemmatizer = WordNetLemmatizer()
        self.pos = pos
        self.endpoints = [self.lemmatizer.lemmatize(end) for end in endpoints]

    def resolveWordToEndpointsBFS(self, word, limit=1000):
        # Brute force search over synonym graph. 
        seen = set()
        toExplore = [word]
        nextLevel = []
        nextLevelSet = set()
        endpointSet = set(self.endpoints)
        exploreCount = 0

        while exploreCount < limit and len(toExplore) > 0:
            current = toExplore.pop()
            if current not in seen:
                seen.add(current)
                current = self.lemmatizer.lemmatize(current)
                # print(current)
                if current in endpointSet:
                    return current
                syns = wn.synsets(current)
                trimmedByPOS = list(filter(lambda x: x.pos() == self.pos, syns))
                synLems = [l.name() for s in trimmedByPOS for l in s.lemmas()]
                # print(synLems)
                unseen = set(filter(lambda x: x not in seen, synLems))
                unseenList = list(filter(lambda x: x not in seen, synLems))
                nextLevelSet |= unseen
                nextLevel.extend(unseenList)
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


if __name__ == "__main__":
    motion_self = ["run", "walk", "jump"]
    motion_other = ["throw", "push", "pull", "carry"]
    stationary = ["rest", "sit", "stand"]
    speak = ["say", "scream", "whisper"]
    usage = ["use"]
    regard = ["examine", "look", "see"]
    being = ["is"]



    endpoints = motion_self + motion_other + stationary + speak + regard + being
    resolver = EndpointResolver('v', endpoints)
    testWord = "embody"

    result1 = resolver.resolveWordToEndpointsBFS(testWord, 1000)
    print("BFS: " + result1)

    result2 = resolver.resolveWordToEndpointsLCH(testWord)
    print("LCH: " + result2)
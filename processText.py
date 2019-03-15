
import nltk.data
import nltk.tag
from nltk import tokenize
from gtts import gTTS
import svo
from svo import findSVOs

import spacy
from spacy.lemmatizer import Lemmatizer


# Scenes are composed of entities, which will be passed to ImageComposer

class Entity:
    def __init__(self, phrase, adjectives, verbPhrase, objs):
        self.name = phrase
        self.root = phrase.root
        self.text = phrase.root.text.lower()   # root word. Generates the base image
        self.adjectives = adjectives           # not usable without search integration
        self.verbPhrase = verbPhrase           # can't be used for image base w/o search
        if not objs:
            self.objs = []                     # Tricky part
        else:
            self.objs = objs

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.root == other.root     # Entity is the same if the roots match
        return False

    def __repr__(self):
        return '\n<\n\t{0}\n\t{1}\n\t{2}\n\t{3}\n>'.format(self.text, self.adjectives, self.verbPhrase, [obj.text for obj in self.objs])

class Setting(Entity):
    # A setting entity is implicitly added to every sentence. 
    # it has special rules

    def __init__(self, adjectives):
        self.root = "&SETTING&"
        self.adjectives = adjectives
        self.verbPhrase = None
        self.predObjs = None    # a setting CONTAINS all other entities

    def __eq__(self, other):
        if isinstance(other, Setting):
            return (self.predObjs == other.predObjs and self.adjectives == other.adjectives) # Entity is the same if the names match
        return False





# The basic informational unit of the TTI system

class Scene:
    def __init__(self, sentenceGroup, entities, depTrees):
        self.sentenceGroup = sentenceGroup
        self.entities = entities
        self.depTrees = depTrees


# Takes in a fullText object and splits the sentences into sentence groups
# Also keeps annotations of the sentences
# A scene is essentially a tuple of a sentence group, entities, dep graph

class Cursor:

    def __init__(self, items):
        self.pool = []
        self.index = 1
        self.items = items
        self.pool.append(items[0])

    def next(self):
        if len(self.pool) > 2:
            self.pool = self.pool[1:]
        if self.index < len(self.items):
            self.pool.append(self.items[self.index])
        self.index += 1
        return self.pool



        

class Script:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.neu = spacy.load('en_coref_md') # https://github.com/huggingface/neuralcoref
        self.lemmatizer = Lemmatizer()
        self.raw = None
        self.sentences = None
        self.sentenceEntitySet = None

    def processEntities(self, text):
        self.raw = text
        doc = self.nlp(text)
        self.sentences = list(doc.sents)

        sentenceEntityLists = []

        # for purposes of anaphora resolution, cursor will be up to 1 behind to 1 ahead.
        cursor = Cursor(self.sentences)
        current_aliases = {}
        perm_aliases = {}
        text2ent = {}


        for sentence in self.sentences:
            nameSet = set()
            sentenceEntityList = []
            aliases = {}
            cursorString = " ".join([st.text for st in cursor.next()])
            print(cursorString)
            sendoc = self.nlp(sentence.text)
            clusters = self.neu(cursorString)._.coref_clusters
            if clusters:
                print(clusters)
                for cluster in clusters:
                    main = cluster.main
                    for mention in cluster.mentions: # mentions are spans
                        if mention.text.lower() != main.text.lower(): # repeated pronoun
                            current_aliases[mention.text.lower()] = main
                            # Above line basically makes sure pronouns are attached
                            perm_aliases[mention] = main
            concat = ""
            for np in sendoc.noun_chunks:
                if np._.coref_cluster:
                    np = np._.coref_cluster.main
                else:
                    resolved = resolveAliasToSpan(current_aliases, np.text.lower())
                    if resolved:
                        np = resolved

                textEnt = np.root.text
                entity = Entity(np, None, None, None)
                # nameSet.add(entity)
                text2ent[entity.text] = entity
                sentenceEntityList.append(entity)

                #fullEntitySet.add(np.root.text.lower())
                #senEntitySet.add(np.r

            svoTriples = findSVOs(sendoc)
            # At this point, we'd want to do 

            for subject, verb, obj in svoTriples:
                resolvedSubject = resolveAliasToText(current_aliases, subject)
                resolvedObject = resolveAliasToText(current_aliases, obj)

                resolvedSubjEntity = None
                resolvedObjEntity = None
                if resolvedSubject in text2ent:
                    resolvedSubjEntity = text2ent[resolvedSubject]
                if resolvedObject in text2ent:
                    resolvedObjEntity = text2ent[resolvedObject]
                if resolvedSubjEntity:
                    if resolvedObjEntity:
                        resolvedSubjEntity.verbPhrase = verb
                        resolvedSubjEntity.objs.append(resolvedObjEntity)

            
            print(current_aliases)
            print(svoTriples)
            print("EntityList:")
            print(sentenceEntityList)
            print("-------------------------------------------------")

            sentenceEntityLists.append(sentenceEntityList)

        self.sentenceEntityLists = sentenceEntityLists # We now have entities in each sentence

        # for enSet in sentenceEntitySets:
            # print(enSet)

    def GroupSentencesByEntities(self):
        #cursor = Cursor(self.sentenceEntitySet)

        #for sentence, entitySet in zip(self.sentences, self.sentence):
        pass

        


    def readFromFile(self, file):
        data = open(file).read()
        process(data)

# takes in text, returns span. If no alias for text, returns None
def resolveAliasToSpan(current_aliases, original):
    resolvedText = original
    if resolvedText in current_aliases:
        while resolvedText in current_aliases:
            resolved = current_aliases[resolvedText]
            if resolvedText == resolved.text.lower():
                break
            resolvedText = resolved.text.lower()
        return resolved
    else:
        return None

# takes in text, returns text. If no alias for text, returns input
def resolveAliasToText(current_aliases, original):
    resolvedText = original
    while resolvedText in current_aliases:
        resolved = current_aliases[resolvedText]
        if resolvedText == resolved.text.lower():
            break
        resolvedText = resolved.text.lower()
    return resolvedText


def computeOptimalDividers(maxDivisionSize, similarityScore):
    pass

        

if __name__ == "__main__":

    s = Script().processEntities("Bob dropped the wrench onto the floor."
        + "It made a loud clang, and Andy yelped in surprise. "
        + "He then broke the window. Johnny grabbed the broom and dustpan. ")


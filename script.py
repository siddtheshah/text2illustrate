
from stanfordcorenlp import StanfordCoreNLP
from collections import defaultdict
import spacy
from spacy.lemmatizer import Lemmatizer



# Scenes are composed of entities, which will be passed to ImageComposer

class Entity:
    def __init__(self, phrase):
        self.text = phrase
        self.adjectives = []           # not usable without search integration
        self.baseVerbs = []             # can't be used for image base w/o search
        self.preps = []
        self.objs = []
        self.ne_annotation = None

    # def __eq__(self, other):
    #     if isinstance(other, Entity):
    #         return self.text == other.text     # Entity is the same if the roots match
    #     return False

    def __repr__(self):
        return '\n<\n\ttext: {0}\n\tadjectives: {1}\n\tbaseVerbs: {2}\n\tpreps: {3}\n\tobjs: {4}\n\tne_ann: {5}\n>'.format(
            self.text, self.adjectives, self.baseVerbs, self.preps, [obj.text for obj in self.objs], self.ne_annotation)

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



# Takes in a fullText object and splits the sentences into sentence groups
# Also keeps annotations of the sentences
# A scene is essentially a tuple of a sentence group, entities, dep graph

class Scene:
    def __init__(self, sentenceGroup, entities, depTrees):
        self.sentenceGroup = sentenceGroup
        self.entities = entities
        self.depTrees = depTrees

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
        self.nlp = StanfordCoreNLP('http://localhost', port=9000)
        self.spacy = spacy.load('en_core_web_sm')
        self.rawText = None
        self.sentences = None
        self.text2ent = defaultdict(None)
        self.lemmatizer = Lemmatizer()


    def processEntities(self, text):
        self.rawText = text
        doc = self.spacy(text)
        self.sentences = list(doc.sents)
        self.allNamedEnts = list(set([e.text for e in doc.ents]))

        ner_raw = self.nlp.get_raw('ner', text)
        # print(ner_raw)
        # ner = self.nlp.ner(text)
        # print(ner)
        extractedRelations = self.nlp.openie(text)
        # self.nlp.show_raw('openie', text)

        # print(extractedRelations)
        coref_raw = self.nlp.get_raw('coref', text)
        representativeMentionsDict = {}


        for co_id, chain in coref_raw['corefs'].items():
            # co is a list
            # print(chain)
            representative = list(filter(lambda x: x['isRepresentativeMention'] == True, chain))[0]
            noun = representative['text']

            # extract root noun if the whole phrase is not a named entity.
            if noun not in self.allNamedEnts:
                tokens = self.nlp.pos_tag(noun)
                for word, tag in tokens:
                    if tag[0:2] == "NN":
                        noun = word.lower() #self.nlp.lemma(word)[0][1]
            for ref in chain:
                print(ref)
                # I'm as clueless as you when it comes to why endIndex is messed up
                representativeMentionsDict[(ref['text'], ref['sentNum'], ref['startIndex'], ref['endIndex'])] = noun

        print(representativeMentionsDict)
        # Syntactical Entites are represented as (text, sentence#, [spanStart, spanEnd])
        #self.sentences = self.nlp.openie(text)

        sentenceEntityLists = []
        namedEnts = []


        for k, sentence in enumerate(self.sentences):
            pos_tags = self.nlp.pos_tag(sentence.text)
            # print(pos_tags)
            entStrings = set()
            sendoc = self.spacy(sentence.text)

            namedEnts.extend([e.text for e in sendoc.ents])
            # print(namedEnts)
            # Replace with stanford impl.
            for np in sendoc.noun_chunks:
                # print(np.root)
                # print(list(np.root.children))
                adjToks = list(filter(lambda x: x.pos_ == "ADJ", list(np.root.children)))
                adjectives = [tok.lemma_ for tok in adjToks]
                # print(adjectives)
                ne_annotation = {}
                if np.text in namedEnts:
                    textEnt = np.text
                else:
                    syntacticalRep = (np.root.text, k+1, np.start +1 , np.end + 1)
                    print(syntacticalRep)
                    if syntacticalRep in representativeMentionsDict:
                        textEnt = representativeMentionsDict[syntacticalRep]
                    else:
                        textEnt = np.root.text
                entity = Entity(textEnt)
                entString = entity.text
                entity.adjectives = adjectives
                if entString not in entStrings:
                    self.text2ent[entString] = entity # May or may not cause issues
                    entStrings.add(entString)                    

            # print(extractedRelations[k])

            unduplicated = []
            for subj, verb, obj in extractedRelations[k]:
                if subj[0] not in self.allNamedEnts and subj in representativeMentionsDict:
                    resolvedSubjectString = representativeMentionsDict[subj]
                else:
                    resolvedSubjectString = subj[0] 
                if obj[0] not in self.allNamedEnts and obj in representativeMentionsDict:
                    resolvedObjectString = representativeMentionsDict[obj]
                else:
                    resolvedObjectString = obj[0]
                print("Resolved:")
                print(resolvedSubjectString)
                print(verb)
                print(resolvedObjectString)

                reducedSubjString = self.getReduceString(namedEnts, resolvedSubjectString)
                reducedObjString = self.getReduceString(namedEnts, resolvedObjectString)
                resolvedSubjEntity = None
                resolvedObjEntity = None
                if reducedSubjString in self.text2ent:
                    resolvedSubjEntity = self.text2ent[reducedSubjString]
                if reducedObjString in self.text2ent:
                    resolvedObjEntity = self.text2ent[reducedObjString]

                if resolvedSubjEntity:
                    if resolvedObjEntity:
                        wordTags = self.nlp.pos_tag(verb)
                        bv = verb
                        prep = ""

                        for word, tag in wordTags:
                            if tag[0:2] == "VB":
                                bv = self.nlp.lemma(word)[0][1]
                            elif tag[0:2] == "IN" or tag[0:2] == "TO":
                                prep = self.nlp.lemma(word)[0][1]
                        triple = (prep, bv, resolvedObjEntity.text)
                        if triple not in unduplicated:
                            resolvedSubjEntity.preps.append(prep)
                            resolvedSubjEntity.baseVerbs.append(bv)
                            resolvedSubjEntity.objs.append(resolvedObjEntity)
                            unduplicated.append(triple)
                    else:
                        print("Unresolved ObjEntity")
                else:
                    print("Unresolved SubjEntity")


            sentenceEntityList = list(self.text2ent[text] for text in entStrings).copy()

            # print("EntityList:")
            # print(sentenceEntityList)
            # print("-------------------------------------------------")

            sentenceEntityLists.append(sentenceEntityList)

        self.sentenceEntityLists = sentenceEntityLists # We now have entities in each sentence
        print(self.sentenceEntityLists)


    def CreateContinuum(self):
        previousDict = {}
        self.continuum = []
        for index, sentenceEntityList in enumerate(self.sentenceEntityLists):
            currentTexts = set([entity.text for entity in sentenceEntityList])
            prevTexts = previousDict.keys()
            displayed = []
            if len(set(prevTexts).intersection(currentTexts)) == 0:
                previousDict = {} # If nothing's retained, blank slate
            else:
                popList = []
                for text, entityTiming in previousDict.items():
                    if index - entityTiming[1] > 1:
                        popList.append(text)
                for text in popList:
                    previousDict.pop(text, None) 

            for entity in sentenceEntityList:
                previousDict[entity.text] = (entity, index) # Overwrites old versions if present
            for entityText in previousDict:
                displayed.append(previousDict[entityText][0])
            self.continuum.append(displayed.copy())
        print(self.continuum)
        # Don't carry over entities that 
    
    def readFromFile(self, file):
        data = open(file).read()
        process(data)

    # inp is a string that we wish to match to an entity.

    def getReduceString(self, NEs, inp):
        if inp in NEs:
            reduceString = inp
        else:
            wordTags = self.nlp.pos_tag(inp)
            for word, tag in wordTags:
                #print(word[0:1])
                if tag[0:2] == "NN":
                    reduceString = self.lemmatizer(word, "NOUN")[0]
                    print("Reduced: " + reduceString)  
                    return reduceString
            reduceString = inp
        print("Reduced: " + reduceString)           
        return reduceString




if __name__ == "__main__":
    s = Script()
    s.processEntities("Bob dropped the wrench onto the floor. "
        + "It made a loud clang, and Andy yelped in surprise. "
        + "He then broke the window. Johnny grabbed the broom and dustpan. ")

    # s.processEntities("Bob dropped the wrench onto the floor. He kept walking toward the hallway, not caring.")
    # s = Script().processEntities("Rocks fell from the sky. Leanne's friends scrambled to dodge the incoming stones.")
    
    # s.processEntities("The nimble rabbit jumped over the log. The fox chased it relentlessly.")
    
    # Named entity tests
    # s = Script().processEntities("John Marston walked down the dusty road. A lonely cactus greeted him.")
    # s.processEntities("Bob was chewing on some apples. Andy wanted to share them. He was getting annoyed, so he left the room")

    # adjective tests
    # s = Script().processEntities("The nimble rabbit jumped over the log.")
    # s = Script().processEntities("The cat was small.")

    # Blank slating
    # s.processEntities("The nimble rabbit jumped over the log. The fox turned and chased the chicken instead.")
    
    print("Continuum: ")
    s.CreateContinuum()
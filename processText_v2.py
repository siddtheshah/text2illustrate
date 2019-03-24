
from stanfordcorenlp import StanfordCoreNLP
from collections import defaultdict
import spacy



# Scenes are composed of entities, which will be passed to ImageComposer

class Entity:
    def __init__(self, phrase):
        self.text = phrase
        self.adjectives = []           # not usable without search integration
        self.baseVerbs = []             # can't be used for image base w/o search
        self.preps = []
        self.objs = []

    # def __eq__(self, other):
    #     if isinstance(other, Entity):
    #         return self.text == other.text     # Entity is the same if the roots match
    #     return False

    def __repr__(self):
        return '\n<\n\t{0}\n\t{1}\n\t{2}\n\t{3}\n\t{4}\n>'.format(
            self.text, self.adjectives, self.baseVerbs, self.preps, [obj.text for obj in self.objs])

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
        self.sentenceEntitySet = None
        self.text2ent = defaultdict(None)

    def processEntities(self, text):
        self.rawText = text
        doc = self.spacy(text)
        self.sentences = list(doc.sents)

        raw = self.nlp.get_raw('ner', text)
        # print(raw)
        extractedRelations = self.nlp.openie(text)
        # self.nlp.show_raw('openie', text)

        # print(extractedRelations)
        coref_raw = self.nlp.get_raw('coref', text)
        representativeMentionsDict = {}
        for co_id, chain in coref_raw['corefs'].items():
            # co is a list
            # print(chain)
            representative = list(filter(lambda x: x['isRepresentativeMention'] == True, chain))[0]
            val = representative['text']
            for ref in chain:
                representativeMentionsDict[(ref['text'], ref['sentNum'], ref['startIndex'], ref['endIndex'])] = val

        # Syntactical Entites are represented as (text, sentence#, [spanStart, spanEnd])


        #self.sentences = self.nlp.openie(text)

        sentenceEntityLists = []


        for k, sentence in enumerate(self.sentences):
            nameSet = set()
            pos_tags = self.nlp.pos_tag(sentence.text)
            # print(pos_tags)
            sentenceEntityList = []
            sendoc = self.spacy(sentence.text)

            namedEnts = [e.text for e in sendoc.ents]
            # sentenceEntityList.extend([Entity(textEnt) for textEnt in namedEnts])
            textEnts = namedEnts
            print(namedEnts)
            # Replace with stanford impl.
            for np in sendoc.noun_chunks:
                if np.text in namedEnts:
                    textEnt = np.text
                else:
                    syntacticalRep = (np.text, k+1, np.start +1 , np.end + 1)
                    # print(syntacticalRep)
                    if syntacticalRep in representativeMentionsDict:
                        textEnt = representativeMentionsDict[syntacticalRep]
                    else:
                        textEnt = np.root.text
                entity = Entity(textEnt)
                debug = entity.text

                self.text2ent[debug] = entity
                if entity not in sentenceEntityList:
                    sentenceEntityList.append(self.text2ent[debug])                    

            print(sentenceEntityList)
            # print(extractedRelations[k])
            unduplicated = []
            for subj, verb, obj in extractedRelations[k]:

                if subj in representativeMentionsDict:
                    resolvedSubjectString = representativeMentionsDict[subj]
                else:
                    resolvedSubjectString = subj[0] 
                if obj in representativeMentionsDict:
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
                        # print(wordTags)
                        bv = ""
                        prep = ""

                        for word, tag in wordTags:
                            # print(tag[0:2])
                            # print(word[0:1])
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


            
            #print(current_aliases)
            #print(svoTriples)
            print("EntityList:")
            print(sentenceEntityList)
            print("-------------------------------------------------")

            sentenceEntityLists.append(sentenceEntityList)

        self.sentenceEntityLists = sentenceEntityLists # We now have entities in each sentence

        # for enSet in sentenceEntitySets:
        #     print(enSet)

    def GroupSentencesByEntities(self):
        #cursor = Cursor(self.sentenceEntitySet)

        #for sentence, entitySet in zip(self.sentences, self.sentence):
        pass

        


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
                    reduceString = word
                    break
        print("Reduced: " + reduceString)           
        return reduceString




if __name__ == "__main__":

    # s = Script().processEntities("Bob dropped the wrench onto the floor."
    #     + "It made a loud clang, and Andy yelped in surprise. "
    #     + "He then broke the window. Johnny grabbed the broom and dustpan. ")

    # s = Script().processEntities("Bob dropped the wrench onto the floor. He kept walking toward the hallway, not caring.")
    # s = Script().processEntities("Rocks fell from the sky. Leanne's friends scrambled to dodge the incoming stones.")
    s = Script().processEntities("Melvin rode a bike to the mall.")
    
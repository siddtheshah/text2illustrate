from nltk.stem.wordnet import WordNetLemmatizer
import spacy

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
OBJECTS = ["dobj", "dative", "attr", "oprd", "pobj"]


# credit to https://github.com/NSchrading/intro-spacy-nlp/blob/master/subject_object_extraction.py

def getSubsFromConjunctions(subs):
    moreSubs = []
    for sub in subs:
        # rights is a generator
        rights = list(sub.rights)
        rightDeps = {tok.lower_ for tok in rights}
        if "and" in rightDeps:
            moreSubs.extend([tok for tok in rights if tok.dep_ in SUBJECTS or tok.pos_ == "NOUN"])
            if len(moreSubs) > 0:
                moreSubs.extend(getSubsFromConjunctions(moreSubs))
    return moreSubs

def getObjsFromConjunctions(objs):
    moreObjs = []
    for obj in objs:
        # rights is a generator
        rights = list(obj.rights)
        rightDeps = {tok.lower_ for tok in rights}
        if "and" in rightDeps:
            moreObjs.extend([tok for tok in rights if tok.dep_ in OBJECTS or tok.pos_ == "NOUN"])
            if len(moreObjs) > 0:
                moreObjs.extend(getObjsFromConjunctions(moreObjs))
    return moreObjs

def getVerbsFromConjunctions(verbs):
    moreVerbs = []
    for verb in verbs:
        rightDeps = {tok.lower_ for tok in verb.rights}
        if "and" in rightDeps:
            moreVerbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
            if len(moreVerbs) > 0:
                moreVerbs.extend(getVerbsFromConjunctions(moreVerbs))
    return moreVerbs

def findSubs(tok):
    head = tok.head
    while head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head:
        head = head.head
    if head.pos_ == "VERB":
        subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
        if len(subs) > 0:
            verbNegated = isNegated(head)
            subs.extend(getSubsFromConjunctions(subs))
            return subs, verbNegated
        elif head.head != head:
            return findSubs(head)
    elif head.pos_ == "NOUN":
        return [head], isNegated(tok)
    return [], False

def isNegated(tok):
    negations = {"no", "not", "n't", "never", "none"}
    for dep in list(tok.lefts) + list(tok.rights):
        if dep.lower_ in negations:
            return True
    return False

def findSVs(tokens):
    svs = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB"]
    for v in verbs:
        subs, verbNegated = getAllSubs(v)
        if len(subs) > 0:
            for sub in subs:
                svs.append((sub.orth_, "!" + v.orth_ if verbNegated else v.orth_))
    return svs

def getObjsFromPrepositions(deps):
    objs = []
    for dep in deps:
        if dep.pos_ == "ADP" and dep.dep_ == "prep":
            objs.extend([tok for tok in dep.rights if tok.dep_  in OBJECTS or tok.lower_ == "me"])
    return objs

def getObjsFromAttrs(deps):
    for dep in deps:
        if dep.pos_ == "NOUN" and dep.dep_ == "attr":
            verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
            if len(verbs) > 0:
                for v in verbs:
                    rights = list(v.rights)
                    objs = [tok for tok in rights if tok.dep_ in OBJECTS]
                    objs.extend(getObjsFromPrepositions(rights))
                    if len(objs) > 0:
                        return v, objs
    return None, None

def getObjFromXComp(deps):
    for dep in deps:
        if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
            v = dep
            rights = list(v.rights)
            objs = [tok for tok in rights if tok.dep_ in OBJECTS]
            objs.extend(getObjsFromPrepositions(rights))
            if len(objs) > 0:
                return v, objs
    return None, None

def getAllSubs(v):
    verbNegated = isNegated(v)
    rights = list(v.rights)
    subs = [tok for tok in rights if tok.dep_ in SUBJECTS and tok.pos_ != "DET"]
    if len(subs) > 0:
        subs.extend(getSubsFromConjunctions(subs))
    else:
        foundSubs, verbNegated = findSubs(v)
        subs.extend(foundSubs)
    return subs, verbNegated

def getAllObjs(v):
    # rights is a generator
    objs = [tok for tok in v.lefts if tok.dep_ in OBJECTS]
    lefts = v.lefts
    objs.extend(getObjsFromPrepositions(lefts))

    potentialNewVerb, potentialNewObjs = getObjFromXComp(lefts)
    if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
        objs.extend(potentialNewObjs)
        v = potentialNewVerb
    if len(objs) > 0:
        objs.extend(getObjsFromConjunctions(objs))
    return v, objs

def findOVSs(tokens):
    ovss = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
    for v in verbs:
        subs, verbNegated = getAllSubs(v)
        print(subs)
        # hopefully there are subs, if not, don't examine this verb any longer
        if len(subs) > 0:
            v, objs = getAllObjs(v)
            print(objs)
            for sub in subs:
                for obj in objs:
                    objNegated = isNegated(obj)
                    ovss.append((sub.lower_, "!" + v.lower_ if verbNegated or objNegated else v.lower_, obj.lower_))
    return ovss

def printDeps(toks):
    for tok in toks:
        print(tok.orth_, tok.dep_, tok.pos_, tok.head.orth_, [t.orth_ for t in tok.lefts], [t.orth_ for t in tok.rights])

def getOVSs(sentence, nlpModel):
    tok = nlpModel(sentence)
    return findOVSs(tok)

def testOVSs():
    nlp = spacy.load('en_core_web_md')


    # print("--------------------------------------------------")
    # tok = nlp("I had been given a watch by Tom.")
    # ovss = findOVSs(tok)
    # printDeps(tok)
    # assert set(ovss) == {('Tom', 'given', 'I')}

    # print("--------------------------------------------------")
    # tok = nlp("It was given to me by someone I admire.")
    # ovss = findOVSs(tok)
    # printDeps(tok)
    # assert set(ovss) == {('someone', 'given', 'me')}

    print("--------------------------------------------------")
    tok = nlp("Was he killed by you?")
    ovss = findOVSs(tok)
    printDeps(tok)
    print(ovss)

    print("--------------------------------------------------")
    tok = nlp("The marble was polished by a gang of slaves.")
    ovss = findOVSs(tok)
    printDeps(tok)
    print(ovss)


    #print("--------------------------------------------------")
    #tok = nlp("he is an evil man that hurt my child and sister")
    #svos = findOVSs(tok)
    #printDeps(tok)
    #print(svos)
    #assert set(svos) == {('he', 'hurt', 'child'), ('he', 'hurt', 'sister'), ('man', 'hurt', 'child'), ('man', 'hurt', 'sister')}

    # print("--------------------------------------------------")
    # tok = nlp("he told me i would die alone with nothing but my career someday")
    # svos = findOVSs(tok)
    # printDeps(tok)
    # print(svos)
    # assert set(svos) == {('he', 'told', 'me')}

    # print("--------------------------------------------------")
    # tok = nlp("I wanted to kill him with a hammer.")
    # svos = findOVSs(tok)
    # printDeps(tok)
    # print(svos)
    # assert set(svos) == {('i', 'kill', 'him')}

    # print("--------------------------------------------------")
    # tok = nlp("because he hit me and also made me so angry i wanted to kill him with a hammer.")
    # svos = findOVSs(tok)
    # printDeps(tok)
    # print(svos)
    # assert set(svos) == {('he', 'hit', 'me'), ('i', 'kill', 'him')}

    

def main():
    testOVSs()

if __name__ == "__main__":
    main()
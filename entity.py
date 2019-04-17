

class Entity:
    def __init__(self, phrase):
        self.text = phrase
        self.adjectives = []           # not usable without search integration
        self.baseVerbs = []             # can't be used for image base w/o search
        self.origVerbs = []
        self.preps = []
        self.objs = []
        self.ne_annotation = {}
        self.eImage = None

    # def __eq__(self, other):
    #     if isinstance(other, Entity):
    #         return self.text == other.text     # Entity is the same if the roots match
    #     return False

    def absorb(self, entity, replaceName=False):
        if replaceName:
            self.text = entity.text.copy()
            self.ne_annotation = entity.ne_annotation.copy()
            self.eImage = entity.eImage.copy()
        self.adjectives.extend(entity.adjectives.copy())
        for bv in entity.baseVerbs:
            if bv != "is":
                self.baseVerbs.append(bv)
        self.preps.extend(entity.preps.copy())
        for obj in entity.objs:
            if obj.text != self.text:
                self.objs.append(obj)

    def __repr__(self):
        return '\n<\n\ttext: {0}\n\tadjectives: {1}\n\tbaseVerbs: {2}\n\tpreps: {3}\n\tobjs: {4}\n\tne_ann: {5}\n>'.format(
            self.text, self.adjectives, self.baseVerbs, self.preps, [obj.text for obj in self.objs], self.ne_annotation)
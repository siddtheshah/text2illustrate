

class Entity:
    def __init__(self, phrase):
        self.text = phrase
        self.adjectives = []           # not usable without search integration
        self.baseVerbs = []             # can't be used for image base w/o search
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
            self.text = entity.text
            self.ne_annotation = entity.ne_annotation
            self.eImage = entity.eImage
        self.adjectives.extend(entity.adjectives)
        self.baseVerbs.extend(entity.baseVerbs)
        self.preps.extend(entity.preps)
        self.objs.extend(entity.objs)


    def __repr__(self):
        return '\n<\n\ttext: {0}\n\tadjectives: {1}\n\tbaseVerbs: {2}\n\tpreps: {3}\n\tobjs: {4}\n\tne_ann: {5}\n>'.format(
            self.text, self.adjectives, self.baseVerbs, self.preps, [obj.text for obj in self.objs], self.ne_annotation)


class Entity:
    def __init__(self, phrase):
        self.text = phrase
        self.adjectives = []           # not usable without search integration
        self.baseVerbs = []             # can't be used for image base w/o search
        self.preps = []
        self.objs = []
        self.ne_annotation = None
        self.eImage = None

    # def __eq__(self, other):
    #     if isinstance(other, Entity):
    #         return self.text == other.text     # Entity is the same if the roots match
    #     return False

    def __repr__(self):
        return '\n<\n\ttext: {0}\n\tadjectives: {1}\n\tbaseVerbs: {2}\n\tpreps: {3}\n\tobjs: {4}\n\tne_ann: {5}\n>'.format(
            self.text, self.adjectives, self.baseVerbs, self.preps, [obj.text for obj in self.objs], self.ne_annotation)
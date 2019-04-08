import spacy
import tkinter as tk
from tkinter import *
from pathlib import Path

class HighlightSupportedNounsText(tk.Text):
    '''A text widget with a new method, highlight_pattern()

    example:

    text = CustomText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")

    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    '''
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self.nlp = spacy.load('en_core_web_sm')
        self.tag_configure("invalid", foreground="#FFFF00", background="#FF0000")
        self.tag_configure("valid", background="#44FF44")


    def checkNouns(self, text):
        doc = self.nlp(text)
        for np in doc.noun_chunks:
            query = np.root.lemma_
            count = self.checkSample(query)
            root = np.root
            start = root.idx
            end = root.idx + len(root.text)
            self.mark_set("matchStart", "1.0+%sc" % start)
            self.mark_set("matchEnd", "1.0+%sc" % end)
            if root.pos_ != "PRON":
                if count > 0:
                    self.tag_add("valid", "matchStart", "matchEnd")
                else:
                    self.tag_add("invalid", "matchStart", "matchEnd")

    # Mock method. Replace with call to visual database.
    def checkSample(self, query):
        file = Path("images/" + query + ".png")
        if file.is_file():
            return 1
        else:
            return 0

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")


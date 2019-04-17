import spacy
import tkinter as tk
from tkinter import *
from pathlib import Path
from collections import defaultdict

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
        self.tag_configure("nonspecFound", background="#44FF44")
        self.tag_configure("namedEnt", background="#FFFF00", foreground="#0000FF")
        self.tag_configure("duplicates", background="#FF8800")

    def copy(self, event=None):
        self.clipboard_clear()
        text = self.get("sel.first", "sel.last")
        self.clipboard_append(text)
    
    def cut(self, event):
        self.copy()
        self.delete("sel.first", "sel.last")

    def paste(self, event):
        text = self.selection_get(selection='CLIPBOARD')
        self.insert('insert', text)



    def checkNouns(self, text):
        doc = self.nlp(text)
        ents = doc.ents
        nps = defaultdict(list)
        for np in doc.noun_chunks:
            root = np.root
            if root.pos_ == "PRON":
                continue
            start = root.idx
            end = root.idx + len(root.text)
            if np in doc.ents:
                tag = "namedEnt"
            else:
                query = np.root.lemma_
                count = self.checkSample(query)
                if count > 0:
                    tag = "nonspecFound"
                else:
                    tag = "invalid"
            self.mark_set("matchStart", "1.0+%sc" % start)
            self.mark_set("matchEnd", "1.0+%sc" % end)
            self.tag_add(tag, "matchStart", "matchEnd")
            # if root.text.lower() in nps:
            #     self.mark_set("matchStart", "1.0+%sc" % start)
            #     self.mark_set("matchEnd", "1.0+%sc" % end)
            #     self.tag_add("duplicates", "matchStart", "matchEnd")
            #     for start, end in nps[root.text.lower()]:
            #         self.mark_set("matchStart", "1.0+%sc" % start)
            #         self.mark_set("matchEnd", "1.0+%sc" % end)
            #         self.tag_add("duplicates", "matchStart", "matchEnd")
            # nps[root.text.lower()].append((start, end))


    # Mock method. Replace with call to visual database.
    def checkSample(self, query):
        for i in range(5):
            file = Path("images/" + query + str(i) + ".png")
            if file.is_file():
                return 1
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


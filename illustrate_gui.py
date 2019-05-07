import tkinter as tk
from tkinter import *
from t2i import *
import time
from threading import Lock, Thread
from PIL import Image, ImageTk
import numpy as np
import cv2
# import Queue

# DRAW_LOCK_ = Lock()
# BUTTON_LOCK_ = Lock()

# class TextQueryThread(threading.Thread):
#     def __init__(self, visualizer, sceneBuffer, text, drawFunc):
#         threading.Thread.__init__(self)
#         self.text = text
#         self.drawFunc = drawFunc
#         self.sceneBuffer = sceneBuffer
#         self.visualizer = visualizer

#     def run(self):
#         self.visualizer.DrawStoryWithCallback(text, drawFunc)

class Text2Illustrate(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        var = StringVar()
        # self.previewTimer = ResettableTimer(5, self.check_input)
        # var.trace("w", lambda start=True : self.previewTimer.reset(start))
        self.highlightText = HighlightSupportedNounsText(self, height=3, width=100)
        # self.highlightText.bind(var)
        # var.set("The man stood on a box.")
        # self.highlightText.insert(END, "John rode his bicycle to the store. He met a woman there named Kate. She brought her dog with her.")
        self.highlightText.insert(END, "There was a box, a ball, a dog, and a cat.")
        self.preview = tk.Button(self, text="Preview", command=self.check_input)
        self.button = tk.Button(self, text="Submit", command=self.submit_button)
        self.canvas = Canvas(self, width=visualizer.CANVAS_WIDTH, height=visualizer.CANVAS_HEIGHT, bg="white")
        self.label = Label(self, text="Enter text, and submit for illustration! (Preview to make sure we have the images)")
        self.label.pack()
        self.highlightText.pack()
        self.preview.pack()
        self.button.pack()
        self.canvas.pack()
        self.sceneBuffer = []
        self.resolve = 0
        self.threads = []
        self.images = []
        self.waitForFinish = True

    def check_input(self):
        self.highlightText.checkNouns(self.highlightText.get("1.0", END))
        # self.previewTimer = ResettableTimer(self.check_input)

    def submit_button(self):
        self.count = 0
        self.visualizer = visualizer.Visualizer()
        text = self.highlightText.get("1.0", END)
        for thread in self.threads:
            thread.join()
        thread = Thread(target=self.visualizer.DrawStoryWithCallback, 
             args= (text, self.scene_callback))
        # BUTTON_LOCK_.acquire()
        self.threads.append(thread)
        thread.start()

        # thread.join()
        # BUTTON_LOCK_.release()
        # self.visualizer.DrawStoryWithCallback(text, self.scene_callback)

    def scene_callback(self, scene):
        self.sceneBuffer.append(scene)
        # print("Need draw lock acquired")
        # DRAW_LOCK_.acquire()
        # print("draw lock acquired")
        scene = self.sceneBuffer.pop(0)
        self.draw_static_scene(scene)
        # print("Need draw lock release")
        # DRAW_LOCK_.release()
        # for thread in self.threads:
        #     thread.join()
        time.sleep(5)
        # print("draw lock released")

    def draw_static_scene(self, scene):
        self.count += 1
        self.canvas.delete("all")
        scene = sorted(scene, key=lambda x: x.eImage.layer)
        for entity in scene:
            self.canvas.create_text(100,10,fill="darkblue", text="Scene " + str(self.count))
            eImage = entity.eImage
            if eImage.image is not None:
                im = Image.fromarray(eImage.image)
                # im.save(entity.text + ".png", "PNG")
                # im = im.resize(im.size, Image.ANTIALIAS)
                imgtk = ImageTk.PhotoImage(image=im.convert("RGBA"))
                self.images.append(imgtk)

                # print("Reached opencv check")
                self.canvas.create_image((eImage.x, eImage.y), image=imgtk)
                #self.canvas.create_image((eImage.x, eImage.y), image=imgtk)
                
                print("Drew " + entity.text)
        print("Draw Done.")

    def draw_dynamic_scene(self, scene):
        pass




    # def diagnostic(self):
    #     self.threads = [t for t in self.threads if t.isAlive()]
    #     print("Active Threads:" + str(len(self.threads)))
    #     self.after(2000, self.diagnostic)



def execute():
    master = Text2Illustrate()
    # master.after(2000, master.diagnostic)
    master.mainloop()

if __name__ == "__main__":
    execute()

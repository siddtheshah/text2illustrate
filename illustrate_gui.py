import tkinter as tk
from tkinter import *
import visualizer
import time
import asyncio
from threading import Lock, Thread
from PIL import Image, ImageTk


DRAW_LOCK_ = Lock()
BUTTON_LOCK_ = Lock()

class Text2Illustrate(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.entry = tk.Entry(self, width=100)
        self.button = tk.Button(self, text="Submit", command=self.sub_button)
        self.canvas = Canvas(self, width=visualizer.CANVAS_WIDTH, height=visualizer.CANVAS_HEIGHT, bg="white")
        self.visualizer = visualizer.Visualizer()
        self.entry.pack()
        self.canvas.pack()
        self.button.pack()
        self.sceneBuffer = []
        self.buttonPress = 0
        self.resolve = 0

    def sub_button(self):
        text = self.entry.get()
        thread = Thread(target=self.visualizer.DrawStoryWithCallback, 
             args= (text, self.scene_callback))
        # BUTTON_LOCK_.acquire()
        thread.start()
        # thread.join()
        # BUTTON_LOCK_.release()
        # self.visualizer.DrawStoryWithCallback(text, self.scene_callback)

    def scene_callback(self, scene):
        self.sceneBuffer.append(scene)
        print("Need draw lock acquired")
        DRAW_LOCK_.acquire()
        print("draw lock acquired")
        scene = self.sceneBuffer.pop(0)
        self.draw_scene(scene)
        print("Need draw lock release")
        DRAW_LOCK_.release()
        print("draw lock released")

    def draw_scene(self, scene):
        self.canvas.delete("all")
        scene = sorted(scene, key=lambda x: x.eImage.layer)
        for entity in scene:
            eImage = entity.eImage
            if eImage:
                im = Image.fromarray(eImage.image.copy())
                imgtk = ImageTk.PhotoImage(image=im)
                self.canvas.create_image((eImage.x, eImage.y), image=imgtk)




def execute():
    master = Text2Illustrate()
    # back = tk.Frame(master, width=1200, height=800, bg='white')
    # back.pack()
    # canvas = Canvas(master, width=visualizer.CANVAS_WIDTH, height=visualizer.CANVAS_HEIGHT, bg="white")
    # # w.create_rectangle(400, 400, 800, 800, fill="#476042")
    # img = tk.PhotoImage(file="images/beach_ball.png")
    # canvas.create_image((400,400), image=img)
    # Label(master, text="Enter text:").pack()
    # text_input = Entry(master)
    # text_input.pack()
    # canvas.pack()
    master.mainloop()

if __name__ == "__main__":
    execute()

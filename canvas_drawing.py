# Source: https://stackoverflow.com/questions/52146562/python-tkinter-paint-how-to-paint-smoothly-and-save-images-with-a-different

# GUI stuff
from tkinter import *

# Pillow limage lib stuff
import PIL
from PIL import Image, ImageDraw


from abc import ABC, abstractmethod

import PIL.Image

class DrawingInput(ABC):
    @abstractmethod
    def active_paint(self,event):
        pass

    @abstractmethod
    def paint(self,event):
        pass


class MouseDrawingCanvas(DrawingInput):
    def __init__(self, width=640, height=480):
        self.previous_x = None
        self.previous_y = None
        self.image_number = 0
        self.image = PIL.Image.new('RGB', (width, height), 'white')
        self.root = Tk()
        self.canvas = Canvas(self.root, width=width, height=height, bg="white")
        self.canvas.bind('<1>', self.active_paint)
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.pack(expand=YES, fill=BOTH)
        self.btn_save = Button(text="save", command=self.save)
        self.btn_save.pack()


    def active_paint(self, event):
        self.previous_x = event.x
        self.previous_y = event.y
        self.canvas.bind('<B1-Motion>', self.paint)

    def paint(self, event):
        x, y = event.x, event.y
        self.canvas.create_line((self.previous_x, self.previous_y, x, y), width=1)
        self.draw.line((self.previous_x, self.previous_y, x, y), fill='black', width=1)
        self.previous_x, self.previous_y = x, y



    def run_loop(self):
        self.root.mainloop()


    def save(self):
        filename = f'image_{self.image_number}.png'
        self.image.save(filename)
        self.image_number += 1








if __name__ == '__main__':
    drawing_app = MouseDrawingCanvas()
    drawing_app.run_loop()

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
        self.canvas.bind('<1>', self.click_paint)
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.pack(expand=YES, fill=BOTH)
        self.btn_save = Button(text="save", command=self.save)
        self.btn_save.pack()


    def click_paint(self, event):
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


import zmq
import msgpack
import threading


class GazeDrawingCanvas(DrawingInput):
    def __init__(self, width=640, height=480):
        self.previous_x = None
        self.previous_y = None
        self.image_number = 0
        self.image = PIL.Image.new('RGB', (width, height), 'white')
        self.root = Tk()
        self.canvas = Canvas(self.root, width=width, height=height, bg="white")
        self.draw = ImageDraw.Draw(self.image)
        self.canvas.pack(expand=YES, fill=BOTH)
        self.btn_save = Button(text="save", command=self.save)
        self.btn_save.pack()
        self.is_drawing = False
        self.canvas.bind('<ButtonPress-1>', self.start_drawing)
        self.canvas.bind('<ButtonRelease-1>', self.stop_drawing)

    def start_drawing(self, event):
        self.is_drawing = True

    def stop_drawing(self, event):
        self.is_drawing = False
        self.previous_x = None
        self.previous_y = None

    def active_paint(self, x, y):
        if self.is_drawing:
            x = x * self.canvas.winfo_width()
            y = y * self.canvas.winfo_height()
            if self.previous_x is not None and self.previous_y is not None:
                self.canvas.create_line((self.previous_x, self.previous_y, x, y), width=1)
                self.draw.line((self.previous_x, self.previous_y, x, y), fill='black', width=1)
            self.previous_x, self.previous_y = x, y

    def paint(self, event):
        pass

    def run_loop(self):
        self.root.mainloop()

    def save(self):
        filename = f'image_{self.image_number}.png'
        self.image.save(filename)
        self.image_number += 1

def gaze_listener(drawing_app):
    ctx = zmq.Context()
    pupil_remote = ctx.socket(zmq.REQ)
    ip = 'localhost'
    port = 50020
    pupil_remote.connect(f'tcp://{ip}:{port}')

    pupil_remote.send_string('SUB_PORT')
    sub_port = pupil_remote.recv_string()

    subscriber = ctx.socket(zmq.SUB)
    subscriber.connect(f'tcp://{ip}:{sub_port}')
    subscriber.subscribe('surface')

    while True:
        topic, payload = subscriber.recv_multipart()
        message = msgpack.loads(payload)
        
        for key, value in message.items():
            if key == 'gaze_on_surfaces':
                for gaze_data in value:
                    if 'norm_pos' in gaze_data:
                        x, y = gaze_data['norm_pos']
                        drawing_app.active_paint(x, y)

if __name__ == '__main__':
    drawing_app = GazeDrawingCanvas(width=1920, height=1000)
    gaze_thread = threading.Thread(target=gaze_listener, args=(drawing_app,))
    gaze_thread.daemon = True
    gaze_thread.start()
    drawing_app.run_loop()
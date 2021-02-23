from tkinter import *


class Slider(Frame):
    def __init__(self, time_value, parent=None, init_value_index=0):
        Frame.__init__(self, parent)
        self.time_value = time_value
        self.number = self.time_value[init_value_index][1]
        self.slide = Scale(self, orient=HORIZONTAL, command=self.set_value,
                           fro=0, to=len(self.time_value)-1, font=('Arial', 8), showvalue=0)
        self.slide.set(init_value_index)
        self.text = Label(self,
                          text=self.time_value[init_value_index][0],
                          font=('Arial', 8))
        self.slide.pack()
        self.text.pack()

    def set_value(self, val):
        self.number = self.time_value[int(val)][1]
        self.text.configure(text=self.time_value[int(val)][0])

    def get_value(self):
        return self.number

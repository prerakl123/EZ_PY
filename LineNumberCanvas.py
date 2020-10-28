from tkinter import *
import tkinter as tk


class LineNumberCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.text_widget = None
        self.breakpoints = []

    def connect(self, text_widget):
        self.text_widget = text_widget

    def re_render(self):
        """Re-render the line canvas"""
        self.delete('all') # To prevent drawing over the previous canvas

        temp = self.text_widget.index("@0, 0")
        while True :
            dline= self.text_widget.dlineinfo(temp)
            if dline is None: 
                break
            y = dline[1]
            x = dline[0]
            linenum = str(temp).split(".")[0]

            id = self.create_text(2, y, anchor="nw", text=linenum, font='Consolas 13')

            if int(linenum) in self.breakpoints:                
                x1, y1, x2, y2 = self.bbox(id)
                self.create_oval(x1, y1, x2, y2, fill='red')
                self.tag_raise(id)

            temp = self.text_widget.index("%s+1line" % temp)

    def get_breakpoint_number(self,event):
         if self.find_withtag('current'):
            i = self.find_withtag('current')[0]
            linenum = int(self.itemcget(i,'text'))

            if linenum in self.breakpoints:
                self.breakpoints.remove(linenum)
            else:
                self.breakpoints.append(linenum)
            self.re_render()

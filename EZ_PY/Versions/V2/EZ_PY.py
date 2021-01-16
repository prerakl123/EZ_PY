from tkinter import *


class ButtonNotebook(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.btn_ids = []
        self.btns = []
        # Frame for buttons that will act as tabs for notebook
        self.btn_frame = Frame(self, height=30, width=1300, bg='green')
        # Frame to show text box widgets for each button
        self.text_frame = Frame(self, height=300, width=1300, bg='blue')

        self.btn_frame.grid(row=0, column=0)
        self.text_frame.grid(row=1, column=0, ipady=190)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def left_shift(self):
        pass

    def right_shift(self):
        pass

    def __list__(self):
        return self.btns


class DirectoryFrame(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)


if __name__ == '__main__':
    root = Tk()
    root.geometry('800x500+50+50')
    t = DirectoryFrame(root, height=2000, width=100, bg='pink')
    t.grid(row=0, column=0, sticky='nsew', columnspan=1)
    s = ButtonNotebook(root, height=2000, width=800, bg='red')
    s.grid(row=0, column=1, sticky='nsew', columnspan=2, ipadx=10)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.mainloop()

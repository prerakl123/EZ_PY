import tkinter as tk
import subprocess
import queue
import os
from threading import Thread
from ColorText import ColorText


class Console(tk.Frame):
    def __init__(self, parent=None, console='python', **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.parent = parent

        # create widgets
        self.ttytext = ColorText(self, wrap=tk.WORD)
        self.ttytext.pack(fill=tk.BOTH, expand=True)
        self.ttytext.linenumbers.pack_forget()

        consolepath = os.path.join(os.path.dirname(__file__), "console.py")
        if console == 'cmd':
            self.p = subprocess.Popen(["powershell"], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                      stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            try:
                self.p = subprocess.Popen(["ipython"], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                          stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
            except FileNotFoundError or Exception:
                self.p = subprocess.Popen(['python', consolepath], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                          stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
        # ["jupyter", "qtconsole"]

        # make queues for keeping stdout and stderr whilst it is transferred between threads
        self.outQueue = queue.Queue()
        self.errQueue = queue.Queue()

        # keep track of where any line that is submitted starts
        self.line_start = 0

        # a daemon to keep track of the threads so they can stop running
        self.alive = True
        
        # start the functions that get stdout and stderr in separate threads
        Thread(target=self.readfromproccessout).start()
        Thread(target=self.readfromproccesserr).start()

        # start the write loop in the main thread
        self.writeloop()

        # key bindings for events
        self.ttytext.bind("<Return>", self.enter)
        self.ttytext.bind('<BackSpace>', self.on_bkspace)
        self.ttytext.bind('<Delete>', self.on_delete)
        self.ttytext.bind('<<Copy>>', self.on_copy)
        self.ttytext.bind('<<Paste>>', self.on_paste)
        self.ttytext.bind('<Control-c>', self.on_copy)
        self.ttytext.bind('<Control-v>', self.on_paste)
        # keylist = [f'<{chr(j)}>' for j in range(65, 91)] + [f'<{chr(j)}>' for j in range(97, 123)] + \
        #           ['<KP_Multiply>', '<KP_Divide>', '<KP_Add>', '<KP_Subtract>', '<KP_Decimal>', '<KP_Separator>'] + \
        #           [f'<KP_{j}>' for j in range(0, 10)] + ['<KP_Equal>', '<space>', '<exclam>', '<quotedbl>'] + \
        #           ['<numbersign>', '<dollar>', '<percent>', '<ampersand>', '<quoteright>', '<parenleft>',
        #            '<parenright>', '<asterisk>', '<plus>', '<comma>', '<minus>', '<period>', '<slash>', '<colon>',
        #            '<semicolon>', '<less>', '<equal>', '<greater>', '<question>', '<at>', '<bracketleft>',
        #            '<backslash>', '<bracketright>', '<asciicircum>', '<underscore>', '<quoteleft>', '<braceleft>',
        #            '<bar>', '<braceright>', '<asciitilde>', '<Tab>'] + [f'{j}' for j in range(0, 10)]
        # for i in keylist:
        #     self.ttytext.bind(f'{i}', self.on_key)

    def destroy(self):
        """This is the function that is automatically called when the widget is destroyed."""
        self.alive = False
        # write exit() to the console in order to stop it running
        self.p.stdin.write("exit()\n".encode())
        self.p.stdin.flush()
        # call the destroy methods to properly destroy widgets
        self.ttytext.destroy()
        tk.Frame.destroy(self)
        
    def enter(self, event):
        """The <Return> key press handler"""
        cur_ind = str(self.ttytext.index(tk.INSERT))
        try:
            if int(cur_ind.split('.')[0]) < int(self.ttytext.search(': ', tk.END, backwards=True).split('.')[0]):
                try:
                    selected = self.ttytext.get('sel.first', 'sel.last')
                    if len(selected) > 0:
                        self.ttytext.insert(tk.END, selected)
                        self.ttytext.mark_set(tk.INSERT, tk.END)
                        self.ttytext.see(tk.INSERT)
                        return 'break'
                except:
                    selected = self.ttytext.get(
                        self.ttytext.search(': ', tk.INSERT, backwards=True), tk.INSERT)
                    self.ttytext.insert(tk.END, selected.strip(': '))
                    self.ttytext.mark_set(tk.INSERT, tk.END)
                    self.ttytext.see(tk.INSERT)
                return 'break'
        except:
            pass
        string = self.ttytext.get(1.0, tk.END)[self.line_start:]
        self.line_start += len(string)
        self.p.stdin.write(string.encode())
        self.p.stdin.flush()

    def on_bkspace(self, event):
        pass

    def on_delete(self, event):
        pass

    def on_key(self, event):
        """The typing control (<KeyRelease>) handler"""
        cur_ind = str(self.ttytext.index(tk.INSERT))
        try:
            if int(cur_ind.split('.')[0]) < int(self.ttytext.search(r'In [0-9]?', tk.END, backwards=True).split('.')[0]):
                return 'break'
        except:
            return

    def on_copy(self, event):
        """<Copy> event handler"""
        self.ttytext.clipboard_append(self.ttytext.get('sel.first', 'sel.last'))

    def on_paste(self, event):
        """<Paste> event handler"""
        self.ttytext.insert(tk.INSERT, self.ttytext.clipboard_get())

    def readfromproccessout(self):
        """To be executed in a separate thread to make read non-blocking"""
        while self.alive:
            data = self.p.stdout.raw.read(1024).decode()
            self.outQueue.put(data)

    def readfromproccesserr(self):
        """To be executed in a separate thread to make read non-blocking"""
        while self.alive:
            data = self.p.stderr.raw.read(1024).decode()
            self.errQueue.put(data)

    def writeloop(self):
        """Used to write data from stdout and stderr to the Text widget"""
        # if there is anything to write from stdout or stderr, then write it
        if not self.errQueue.empty():
            self.write(self.errQueue.get())
        if not self.outQueue.empty():
            self.write(self.outQueue.get())

        # run this method again after 10ms
        if self.alive:
            self.after(10, self.writeloop)

    def write(self, string):
        self.ttytext.insert(tk.END, string)
        self.ttytext.see(tk.END)
        self.line_start += len(string)
        self.ttytext.inst_trigger()


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('500x500+100+100')
    main_window = Console(root)
    main_window.pack(fill=tk.BOTH, expand=True)
    main_window.ttytext.focus_force()
    root.mainloop()

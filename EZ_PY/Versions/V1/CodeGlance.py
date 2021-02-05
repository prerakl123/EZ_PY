from tkinter import *
from ColorText import ColorText
from tkinter import ttk


class TextPeer(Text):
    """A peer of an existing text widget"""
    count = 0
    def __init__(self, master, cnf={}, **kw):
        TextPeer.count += 1
        self.master = master
        parent = master.master
        peerName = "peer-{}".format(TextPeer.count)
        if str(parent) == ".":
            peerPath = ".{}".format(peerName)
        else:
            peerPath = "{}.{}".format(parent, peerName)

        # Create the peer
        master.tk.call(master, 'peer', 'create', peerPath, *self._options(cnf, kw))

        # Create the tkinter widget based on the peer
        # We can't call tk.Text.__init__ because it will try to
        # create a new text widget. Instead, we want to use
        # the peer widget that has already been created.
        BaseWidget._setup(self, parent, {'name': peerName})

        # Highlight the current line
        # self.highlight_line()
        # cur_ind = self.master.index(INSERT)

    def highlight_line(self, interval=100):
        self.tag_remove("active_line", 1.0, END)
        self.tag_add("active_line", self.master.index(INSERT+' linestart'), self.master.index(INSERT+' lineend+1c'))
        self.tag_config('active_line', background='gray75')
        print(self.bbox(INSERT))
        self.after(100, self.highlight_line)


def main(win=None):
    if win:
        root = win
    else:
        root = Tk()

    def viewall(*args):
        text1.yview(*args)
        text2.yview(*args)
        print(text1.bbox(CURRENT), text2.bbox(CURRENT), text1.bbox(INSERT), text1.bbox(INSERT))

    def on_mousewheel(event):
        shift = (event.state & 0x1) != 0
        scroll = -1 if event.delta > 0 else 1
        if shift:
            text1.xview_scroll(scroll, "units")
        else:
            text2.yview_scroll(scroll, "pages")
            text1.yview_scroll(scroll, 'units')

    def geom_config(event):
        root.update()
        win_width, win_height = int(root.winfo_geometry().split('x')[0]), int(root.winfo_geometry().split('x')[-1].split('+')[0])
        text1.config(width=int(win_width)//14)
        text2.config(width=int(win_width)//210)

    text1 = ColorText(root)
    text2 = TextPeer(text1, fg='white', bg='black', font='Consolas 6')
    # text3 = TextPeer(text1, width=40, height=8, background="yellow", font=("Fixed", 12))
    rolly = ttk.Scrollbar(root, orient=VERTICAL, command=viewall)
    rolly.selection_own(displayof=text2)

    text1['yscrollcommand'] = rolly.set
    text2['yscrollcommand'] = rolly.set

    text1.pack(side="left", fill="both", expand=True)
    text2.pack(side="right", fill="both", expand=True)
    # text3.pack(side="top", fill="both", expand=True)
    rolly.pack(side='right', fill='y')

    text2.insert("end", (
        "Type in one, and the change will "
        "appear in the other."
    ))
    text1.bind_all('<MouseWheel>', on_mousewheel)
    text2.bind_all('<MouseWheel>', on_mousewheel)
    root.bind('<Configure>', geom_config)
    root.update()
    root.minsize(682, 489)
    root.mainloop()


if __name__ == '__main__':
    main()

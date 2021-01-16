##from tkinter import *
##
##
##class CodeGlance(Text):
##    def __init__(self, master, editor: Text, **kwargs):
##        Text.__init__(self, master, **kwargs)
##        self.peer_create(editor)








from tkinter import *
from ColorText import ColorText
from tkinter import ttk


class TextPeer(Text):
    """A peer of an existing text widget"""
    count = 0
    def __init__(self, master, cnf={}, **kw):
        TextPeer.count += 1
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


root = Tk()


def viewall(*args):
    global text1, text2
    text1.yview(*args)
    text2.yview(*args)

def on_mousewheel(event):
    shift = (event.state & 0x1) != 0
    scroll = -1 if event.delta > 0 else 1
    if shift:
        text1.xview_scroll(scroll, "units")
    else:
        text2.yview_scroll(scroll, "pages")
        text1.yview_scroll(scroll, 'pages')


text1 = ColorText(root, width=60)
text2 = TextPeer(text1, width=10, fg='white', bg='black', font='Consolas 6')
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
root.mainloop()

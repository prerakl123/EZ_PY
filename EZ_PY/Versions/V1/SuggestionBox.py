from time import time
from tkinter import *
import json

NEW = 'new'
APPEND = 'append'


class SuggestionBox(Toplevel):
    """
    Provides a SuggestionBox widget for tkinter.
    SuggestionBox will appear on key combination: <Control-space>.
    """
    def __init__(self, textbox: Text = None, suggestion_list: list = None, sugFont=('Consolas', 10), delay: float = 0.5, event=None):
        """
        Initializing the SuggestionBox
        Arguments:
          textbox:          for EZ_PY this will take the ColorText widget
          suggestion_font:  Font to be used
          delay:            The delay in seconds before the SuggestionBox appears(may be float)
        """
        with open('config.json', 'r') as file:
            self.config_dict = json.load(file)

        self.textbox = textbox

        # The parent of the SuggestionBox is the parent of the SuggestionBox's widget
        self.parent = self.textbox.master

        # initialize the Toplevel
        Toplevel.__init__(self, self.parent, padx=1, pady=1)

        # Hide initially
        self.withdraw()

        # The ToolTip Toplevel should have no frame or title bar
        self.overrideredirect(True)

        # ToolTip should be displayed on the top of everything
        self.wm_attributes('-topmost', True)

        scroll = Scrollbar(self, orient=VERTICAL)
        self.suglist = Listbox(self, width=5, height=10, yscrollcommand=scroll.set)
        scroll.config(command=self.suglist.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.suglist.pack(side=TOP, expand=True, fill=BOTH)

        self.delay = delay
        self.visible = 0
        self.lastMotion = 0

        self.suggestion_list = suggestion_list
        self.insertlist(_list=self.suggestion_list)

        self.textbox.bind('<Control-space>', self.spawn, '+')
        self.textbox.bind('<Escape>', self.hide, '+')
        self.textbox.bind('<Any-KeyPress>', self.move, '+')
        self.suglist.bind('<Return>', self.on_return)

    def hide(self, event=None):
        """
        Hides the SuggestionBox. Usually this is caused by leaving the widget
        Arguments:
          event: The event that called this function
        """
        self.visible = 0
        self.textbox.unbind('<Any-KeyPress>')
        self.withdraw()
        self.destroy()

    def insertlist(self, event=None, _list: list = None, mode=NEW):
        """
        Inserts elements into SuggestionBox.
        Arguments:
          event: event that called this function
          _list: list to be inserted
          mode:  mode for insertion (NEW: deletes previous list and adds the new `_list`
                                     APPEND: appends `_list` to previously present list)
        """
        if mode == NEW:
            self.suglist.delete(0, END)
            self.suggestion_list = _list
            self.suggestion_list.sort()
            self.suglist.insert(END, *self.suggestion_list)
        elif mode == APPEND:
            self.suggestion_list.extend(_list)
            self.suggestion_list.sort()
            self.suglist.delete(0, END)
            self.suglist.insert(END, *self.suggestion_list)

    def move(self, event):
        """
        Processes motion within the widget.
        Arguments:
          event: The event that called this function
        """
        if event.char in [' ', '"', "'", ',', ')']:
            return
        self.lastMotion = time()

        pos_x, pos_y = event.widget.winfo_rootx(), event.widget.winfo_rooty()
        bbox = event.widget.bbox(INSERT)
        bb_x, bb_y, bb_w, bb_h = bbox
        width = 180
        height = 200
        ox = pos_x + bb_x
        oy = pos_y + bb_y + bb_h
        geometry = (width, height, ox, oy)

        self.visible = 1

        # Offset the ToolTip some pixels away form the pointer
        self.geometry("%dx%d%+d%+d" % geometry)
        self.after(int(self.delay * 1000), self.show)

    def on_return(self, event=None):
        txt = self.suglist.selection_get()
        self.textbox.insert(INSERT, txt)
        self.hide()

    def show(self):
        """
        Displays the SuggestionBox if the time delay has been long enough
        """
        if self.visible == 1 and time() - self.lastMotion > self.delay:
            self.visible = 2
            self.suglist.focus()
            self.suglist.select_set(0)
        if self.visible == 2:
            self.deiconify()

    def spawn(self, event=None):
        """
        Spawn the SuggestionBox. This simply makes the SuggestionBox eligible for display.

        Arguments:
          event:  The event that called this function
        """
        self.visible = 1
        self.textbox.bind('<Any-KeyPress>', self.move, '+')
        # The after function takes a time argument in milliseconds
        self.after(int(self.delay * 1000), self.show)


if __name__ == '__main__':
    import keyword as kw
    import pkgutil

    modules = []
    for i in pkgutil.iter_modules():
        modules.append(i.name)
    in_modules = sys.modules.keys()
    modules = list(modules+list(in_modules))
    for i in modules:
        if '[' in i or ']' in i or '(' in i or ')' in i or '{' in i or '}' in i:
            modules.pop(modules.index(i))
    
    root = Tk()
    
    def show_suggbox(e=None):
        SuggestionBox(textbox=t, suggestion_list=kw.kwlist + modules)
    
    t = Text(root, font='Consolas 12')
    t.pack(expand=True, fill=BOTH)
    t.bind('<Control-space>', show_suggbox)
    root.mainloop()

from time import time, localtime, strftime
from tkinter import *


class SuggestionBox(Toplevel):
    """
    Provides a SuggestionBox widget for tkinter.
    SuggestionBox will be applied on pressing left parentheses '(' character.
    """
    def __init__(self, textbox, suggestion_font, delay=0.5, event=None):
        """
        Initializing the SuggestionBox

        Arguments:
          textbox:           As this is exclusively designed for EZ_PY this will take the ColorText widget
          suggestion_font:  Font to be used
          delay:            The delay in seconds before the SuggestionBox appears(may be float)
        """

        self.textbox = textbox
        # The parent of the SuggestionBox is the parent of the SuggestionBox's widget
        self.parent = self.textbox.master
        # initialize the Toplevel
        Toplevel.__init__(self, self.parent, bg='black', padx=1, pady=1)
        # Hide initially
        self.withdraw()
        # The ToolTip Toplevel should have no frame or title bar
        self.overrideredirect(True)
        # The suggestVar will contain the text displayed by the SuggestionBox
        self.suggestVar = StringVar()

        self.delay = delay
        self.visible = 0
        self.lastMotion = 0

    def spawn(self, event=None):
        """
        Spawn the SuggestionBox. This simply makes the SuggestionBox eligible for display.

        Arguments:
          event:  The event that called this function
        """
        self.visible = 1
        # The after function takes a time argument in milliseconds
        self.after(int(self.delay * 1000), self.show)

    def show(self):
        """
        Displays the SuggestionBox if the time delay has been long enough
        """
        if self.visible == 1 and time() - self.lastMotion > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()

    def move(self, event):
        """
        Processes motion within the widget.
        Arguments:
          event: The event that called this function
        """
        self.lastMotion = time()
        # motion within the widget will make the SuggestionBox disappear
        self.withdraw()
        self.visible = 1
        # Offset the ToolTip some pixels away form the pointer
        self.geometry('+%i+%i' % (event.x_root+3, event.y_root-30))
        self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        """
        Hides the SuggestionBox.  Usually this is caused by leaving the widget
        Arguments:
          event: The event that called this function
        """
        self.visible = 0
        self.withdraw()

    def update(self, msg):
        """
        Updates the Tooltip with a new message.
        """
        self.msgVar.set(msg)

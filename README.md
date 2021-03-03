# EZ_PY
A simple Python text editor made using Python, developed by Prerak Lodha

# Description
This simple editor is not complete yet but the main major things that matter like regex for coloring keywords, etc have been completed. This editor may contain support for other languages in future, currently only Python and some amount of HTML can be coded on this. 

MarkDown (\**.md*) files can also created (with live preview).

The working of this text editor is simple as though on running the opening screen wouldn't show anything but two buttons on the left (which are not completely alienated i.e. on 
hovering Tooltip is displayed) which is something I am still working on. On clicking on the '+' button (label actually) a new toplevel window will appear which will ask you to 
choose which file to create. On choosing the type, the file will be opened in the tkinter's Notebook widget as a tab 
> Why Notebook widget?
>
>
>> If you want to open more files of any kind you can open and add more of them into the Notebook as tabs which will be easy to cycle between.

The number of new Python files or simple text files or MarkDownfiles or the number of Consoles you open will be displayed as tab name.

Menubar will be created as soon as a new file is created or opened.

### Shortcut key combinations
If `Ctrl+O` is pressed while current focus is out of the tabs a new tab will be created with filename as tab name, otherwise if the focus is currently inside the editor the file 
may open in the same one (which is like a bug) but once you realize the pattern of things happening you may find it handy.

In the case of `Ctrl+N` the case is mostly the same as `Ctrl+O` instead it creates new blank files.

If `Ctrl+Shift+N` is pressed the 'select the type of file to be created' window will appear.

`Ctrl+Shift+C` will add a console tab.

## Modules used in the project
(BUILT-INS)
```
tkinter
tkinter.ttk
tkinter.messagebox
tkinter.filedialog
tkinter.scrolledtext
json
keywords
builtins
re
code
io
hashlib
queue
sys
time
threading
traceback
contextlib
```
(INSTALLED)
```
markdown2
tkhtmlview
```

# Problems
There can be problems while creating \**.md* files like the preview may scroll back to top.

Docstrings for descriptions not added.

Tab lengths currently have to be defined in the `tab_length` key in `config.json` file.

# Future Updates
More Themes will be updated and the currently defined but not assigned themes will have their color combinations assigned to them.

*fullscreen* in one of the future updates

Tabs and other settings for the editor will be included.

Actual customized notebook widget will be implemented. (not the customized built-in notebook)

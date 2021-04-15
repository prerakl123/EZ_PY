# from idlelib.editor import EditorWindow, IndentSearcher
# from idlelib.autocomplete import AutoComplete
# from idlelib.textview import view_text, ViewFrame
# from idlelib.searchengine import SearchEngine, get
# from idlelib.sidebar import LineNumbers
# from idlelib.delegator import Delegator
# from idlelib.percolator import Percolator
# from idlelib.config import idleConf
from tkinter import *
# import tokenize


root = Tk()
root.bind('<Any-Key>', lambda _=None: print(_))
root.mainloop()
# x = view_text(root, 'Trial', 'Aloo Pakoda is not the best')
# d = ViewFrame(root, 'nope')
# d.pack()
# text_frame = Frame(root)
# text_frame.pack(side=LEFT, fill=BOTH, expand=True)
# text_frame.rowconfigure(1, weight=1)
# text_frame.columnconfigure(1, weight=1)
# font = idleConf.GetFont(root, 'main', 'EditorWindow')
# t = Text(text_frame, width=80, height=24, wrap=NONE, font=font)
# t.grid(row=1, column=1, sticky=NSEW)
# s = SearchEngine(t)
# get(t)


# class Editwin:
#     def __init__(self, text):
#         self.text = text
#         self.text_frame = self.text.master
#         self.per = Percolator(text)
#         self.undo = Delegator()
#         self.per.insertfilter(self.undo)
#
#     def setvar(self, name, value):
#         pass
#
#     def getlineno(self, index):
#         return int(float(self.text.index(index)))


# e = Editwin(t)
# e.vbar = Scrollbar(text_frame)
# ln = LineNumbers(e)
# ln.show_sidebar()
# root.after(3000, lambda x=None: ln.hide_sidebar())




# e = EditorWindow(root=root, filename=None)
# text = e.text_frame


# class App(Tk):
#     text = Text(font='Consolas 13')
#     text.pack()
#
#     def __init__(self, **kwargs):
#         pass
#
#
# a = AutoComplete(App)
# a.












# import ast
#
# mdef = '''
# from tkinter import *
# import randfuncs as r
#
#
# class Pro:
#     def __init__(self, a=1, b=2):
#         print(a, b)
#
# def foo(x):
#     """This function returns 2*x"""
#     return 2*x
#
# def frac(n: str):
#     """This function capitalizes the str `n`"""
#     return n.upper()'''
#
# a = ast.parse(mdef)
# definitions = [[n.name, n.body, n.decorator_list, n.lineno, n.col_offset, n._fields] for n in ast.walk(a) if type(n) in
#                [ast.ClassDef, ast.FunctionDef]]
# mods = [n.body for n in ast.walk(a) if type(n) == ast.Module]
# print(mods)
# for i in definitions:
#     print(i)
# teststring = '''pratapslodhaa@gmail.com is an email address. And preraklodha.12scie@gmail.com is also an address https://www.hotmail.com is a website, 192.168.1.1 is an IP address, https://192.100.17.1 is a just a video feed IP address, http://192.168.1.1/html/quicksetup.html is some Airtel thing. https://www.google.com/search?q=what+is+a+form+feed+character&oq=what+is+a+form+feed+character&aqs=chrome.0.69i59j0i22i30.2578j0j7&sourceid=chrome&ie=UTF-8 is a hell large gmail address, www.aloo.com is the smallest form of URL 1.1.1.4 and -1.2.3.4 and 192.168.100.255 are just some random IPv4 addresses, 2001:0db8:85a3:0000:0000:8a2e:0370:7334 is an IPv6 address, 6384:1319:7700:7631:446A:5511:8940:2552 and 141:0:0:0:15:0:0:1 are just some random IPv6 addresses Examples of MAC address for an Ethernet NIC: 00:0a:95:9d:68:16 or 00-D0-56-F2-B5-12 or 00-26-DD-14-C4-EE or 06-00-00-00-00-00 C:\Users\Prerak\aloopakoda.png, \\server\share\myfile.txt, "Z:\Users\aloopakoda and pickle\poopoo.png" Some: int | floats: 10, 20, 1.4, -8910274.19284 9.12489 ThisIsA CamelCase'''



# from tkinter import *
#
# root = Tk()
# text = Text(root)
# text.insert('1.0', 'This is a cruel is a world is a pakoda is a pani puri is a')
# text.tag_add('isa', '1.1', '1.5')
# text.tag_add('isa', '1.8', '1.10')
# text.tag_add('isa', '1.14', '1.19')
# text.tag_add('isa', '1.23', '1.30')
# text.tag_config('isa', background='#00ff00', underline=True)
# text.pack()
# root.mainloop()





# import tkinter.tix
#
#
# def runsample(w):
#     global root
#     root = w
#
#     # We use these options to set the sizes of the subwidgets inside the
#     # notebook, so that they are well-aligned on the screen.
#     prefix = tkinter.tix.OptionName(w)
#     if prefix:
#         prefix = '*'+prefix
#     else:
#         prefix = ''
#     w.option_add(prefix+'*TixControl*entry.width', 10)
#     w.option_add(prefix+'*TixControl*label.width', 18)
#     w.option_add(prefix+'*TixControl*label.anchor', tkinter.tix.E)
#     w.option_add(prefix+'*TixNoteBook*tagPadX', 8)
#
#     # Create the notebook widget and set its backpagecolor to gray.
#     # Note that the -backpagecolor option belongs to the "nbframe"
#     # subwidget.
#     nb = tkinter.tix.NoteBook(w, name='nb', ipadx=6, ipady=6)
#     nb['bg'] = 'gray'
#     nb.nbframe['backpagecolor'] = 'gray'
#
#     # Create the two tabs on the notebook. The -underline option
#     # puts a underline on the first character of the labels of the tabs.
#     # Keyboard accelerators will be defined automatically according
#     # to the underlined character.
#     nb.add('hard_disk', label="Hard Disk", underline=0)
#     nb.add('network', label="Network", underline=0)
#
#     nb.pack(expand=1, fill=tkinter.tix.BOTH, padx=5, pady=5, side=tkinter.tix.TOP)
#
#     # ----------------------------------------
#     # Create the first page
#     # ----------------------------------------
#     # Create two frames: one for the common buttons, one for the
#     # other widgets
#     #
#     tab = nb.hard_disk
#     f = tkinter.tix.Frame(tab)
#     common = tkinter.tix.Frame(tab)
#
#     f.pack(side=tkinter.tix.LEFT, padx=2, pady=2, fill=tkinter.tix.BOTH, expand=1)
#     common.pack(side=tkinter.tix.RIGHT, padx=2, fill=tkinter.tix.Y)
#
#     a = tkinter.tix.Control(f, value=12,   label='Access time: ')
#     w = tkinter.tix.Control(f, value=400,  label='Write Throughput: ')
#     r = tkinter.tix.Control(f, value=400,  label='Read Throughput: ')
#     c = tkinter.tix.Control(f, value=1021, label='Capacity: ')
#
#     a.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#     w.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#     r.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#     c.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#
#     # Create the common buttons
#     createcommonbuttons(common)
#
#     # ----------------------------------------
#     # Create the second page
#     # ----------------------------------------
#
#     tab = nb.network
#
#     f = tkinter.tix.Frame(tab)
#     common = tkinter.tix.Frame(tab)
#
#     f.pack(side=tkinter.tix.LEFT, padx=2, pady=2, fill=tkinter.tix.BOTH, expand=1)
#     common.pack(side=tkinter.tix.RIGHT, padx=2, fill=tkinter.tix.Y)
#
#     a = tkinter.tix.Control(f, value=12,   label='Access time: ')
#     w = tkinter.tix.Control(f, value=400,  label='Write Throughput: ')
#     r = tkinter.tix.Control(f, value=400,  label='Read Throughput: ')
#     c = tkinter.tix.Control(f, value=1021, label='Capacity: ')
#     u = tkinter.tix.Control(f, value=10,   label='Users: ')
#
#     a.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#     w.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#     r.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#     c.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#     u.pack(side=tkinter.tix.TOP, padx=20, pady=2)
#
#     createcommonbuttons(common)
#
#
# def dodestroy():
#     global root
#     root.destroy()
#
#
# def createcommonbuttons(master):
#     ok = tkinter.tix.Button(master, name='ok', text='OK', width=6, command=dodestroy)
#     cancel = tkinter.tix.Button(master, name='cancel', text='Cancel', width=6, command=dodestroy)
#
#     ok.pack(side=tkinter.tix.TOP, padx=2, pady=2)
#     cancel.pack(side=tkinter.tix.TOP, padx=2, pady=2)
#
#
# if __name__ == '__main__':
#     root = tkinter.tix.Tk()
#     runsample(root)
#     root.mainloop()









# from tkinter import *
# from tkinter import font
#
#
# def white(event=None):
#     start = '1.0'
#     end = text.index(END)
#     while True:
#         if start == end:
#             break
#         ind = text.search(' ', start, end)
#         text.tag_add('white', ind)
#         start = f"{ind}+1c"
#         print(text.tag_ranges('white'))
# def on_control_mswheel(event=None):
#     text_font = _font.actual()
#     if event.delta > 0:
#         if text_font['size'] == 300:
#             return
#         text.config(font=f"{text_font['family']} {int(text_font['size'])+1}")
#         _font.config(size=int(text_font['size'])+1)
#     else:
#         if int(text_font['size']) == 1:
#             return
#         text.config(font=f"{text_font['family']} {int(text_font['size']) - 1}")
#         _font.config(size=int(text_font['size']) - 1)
#     print(text_font, event)
#
#
# root = Tk()
# root.geometry('400x400+40+40')
# text = Text(root, bg='black', fg='white', insertbackground='white')
# text.pack(expand=True, fill=BOTH)
# text.bind('<Control-MouseWheel>', on_control_mswheel)
# _font = font.Font(text)
# text.bind('<space>', white)
# text.tag_config('white', background='#aabbff', foreground='pink')
# root.mainloop()






# import json
#
# with open('./PreviousFiles/config(old).json', 'r') as file:
#     d_dict = json.load(file)
#
# print(d_dict)
# d_dict['color_text_font'] = ['Segoe UI', 100]
#
# with open('./PreviousFiles/config(old).json', 'w') as file2:
#     j_o = json.dumps(d_dict, indent=4)
#     file2.write(j_o)

##from typing import AnyStr, Any, Iterable
##
##
##def soe(a: AnyStr, b: Any) -> Iterable:
##    return list(a) + list(b)
##
##
##print(soe(b'0b01001100001111001001101010001111100000011111000000100100111000000111101101001000010011110001110',
##    ['poopoo', 'peepee', 'tootoo', 'teetee']))


from idlelib.editor import EditorWindow, IndentSearcher
from idlelib.autocomplete import AutoComplete
from idlelib.textview import view_text, ViewFrame
from idlelib.searchengine import SearchEngine, get
from idlelib.sidebar import LineNumbers
from idlelib.delegator import Delegator
from idlelib.percolator import Percolator
from idlelib.config import idleConf
from tkinter import *
import tokenize


# root = Tk()
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


class Editwin:
    def __init__(self, text):
        self.text = text
        self.text_frame = self.text.master
        self.per = Percolator(text)
        self.undo = Delegator()
        self.per.insertfilter(self.undo)

    def setvar(self, name, value):
        pass

    def getlineno(self, index):
        return int(float(self.text.index(index)))


# e = Editwin(t)
# e.vbar = Scrollbar(text_frame)
# ln = LineNumbers(e)
# ln.show_sidebar()
# root.after(3000, lambda x=None: ln.hide_sidebar())




# e = EditorWindow(root=root, filename=None)
# text = e.text_frame


##class App(Tk):
##    text = Text(font='Consolas 13')
##    text.pack()
##    
##    def __init__(self, **kwargs):
##        pass
##
##
##a = AutoComplete(App)
##a.












##import ast
##
##mdef = '''
##from tkinter import *
##import randfuncs as r
##
##
##class Pro:
##    def __init__(self, a=1, b=2):
##        print(a, b)
##        
##def foo(x):
##    """This function returns 2*x"""
##    return 2*x
##
##def frac(n: str):
##    """This function capitalizes the str `n`"""
##    return n.upper()'''
##
##a = ast.parse(mdef)
##definitions = [[n.name, n.body, n.decorator_list, n.lineno, n.col_offset, n._fields] for n in ast.walk(a) if type(n) in
##               [ast.ClassDef, ast.FunctionDef]]
##mods = [n.body for n in ast.walk(a) if type(n) == ast.Module]
##print(mods)
##for i in definitions:
##    print(i)
##teststring = '''pratapslodhaa@gmail.com is an email address. And preraklodha.12scie@gmail.com is also an address https://www.hotmail.com is a website, 192.168.1.1 is an IP address, https://192.100.17.1 is a just a video feed IP address, http://192.168.1.1/html/quicksetup.html is some Airtel thing. https://www.google.com/search?q=what+is+a+form+feed+character&oq=what+is+a+form+feed+character&aqs=chrome.0.69i59j0i22i30.2578j0j7&sourceid=chrome&ie=UTF-8 is a hell large gmail address, www.aloo.com is the smallest form of URL 1.1.1.4 and -1.2.3.4 and 192.168.100.255 are just some random IPv4 addresses, 2001:0db8:85a3:0000:0000:8a2e:0370:7334 is an IPv6 address, 6384:1319:7700:7631:446A:5511:8940:2552 and 141:0:0:0:15:0:0:1 are just some random IPv6 addresses Examples of MAC address for an Ethernet NIC: 00:0a:95:9d:68:16 or 00-D0-56-F2-B5-12 or 00-26-DD-14-C4-EE or 06-00-00-00-00-00 C:\Users\Prerak\aloopakoda.png, \\server\share\myfile.txt, "Z:\Users\aloopakoda and pickle\poopoo.png" Some: int | floats: 10, 20, 1.4, -8910274.19284 9.12489 ThisIsA CamelCase'''



from tkinter import *

root = Tk()
text = Text(root)
text.insert('1.0', 'This is a cruel is a world is a pakoda is a pani puri is a')
text.tag_add('isa', '1.1', '1.5')
text.tag_add('isa', '1.8', '1.10')
text.tag_add('isa', '1.14', '1.19')
text.tag_add('isa', '1.23', '1.30')
text.tag_config('isa', background='#00ff00', underline=True)
text.pack()
root.mainloop()

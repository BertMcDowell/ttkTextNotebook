# -*- coding: utf-8 -*-

# Copyright (c) Bert McDowell 2020
# For license see LICENSE
from tkinter import *
from tkinter import ttk

class TextNotebook(ttk.Frame):
    __inititialized = False
    __style = None
    __config_tab_active = None
    __config_tab_inactive = None

    def __initialize_custom_style(self):
        TextNotebook.__style = ttk.Style()
        TextNotebook.__style.configure('TextNotebook.Tabs.TFrame', background='gray69')

        TextNotebook.__config_tab_active = {
                'bg':'gray79',
                'activebackground':'gray69',
                'borderwidth':2, 
                'pady':5, 
                'disabledforeground':'black',
                'state':DISABLED, 
                'font':'Helvetica 8 bold'
                }
        TextNotebook.__config_tab_inactive = {
                'bg':'gray69',
                'activebackground':'gray79',
                'borderwidth':1, 
                'pady':2, 
                'disabledforeground':'black',
                'state':NORMAL, 
                'font':'Helvetica 8'
                }

    def __init__(self,parent,*args,**kwargs):
        if not TextNotebook.__inititialized:
            self.__initialize_custom_style()
            TextNotebook.__inititialized = True

        ttk.Frame.__init__(self, parent, *args)

        self._topFrame = ttk.Frame(master=self)
        self._topFrame.pack(fill=X, pady=0)

        self._navFrame = ttk.Frame(master=self._topFrame)
        leftArrow = Button(self._navFrame, text="\u25c0", width=1, relief=FLAT, repeatdelay=500, repeatinterval=100)
        leftArrow.bind("<Button-1>", self._tabs_slide_left)
        leftArrow.pack(side=LEFT, expand=True)
        rightArrow = Button(self._navFrame, text=" \u25b6", width=1, relief=FLAT, repeatdelay=500, repeatinterval=100)
        rightArrow.bind("<Button-1>", self._tabs_slide_right)
        rightArrow.pack(side=RIGHT, expand=True)
        self._navFrame.pack(side=RIGHT, pady=0)

        self._tabFrame = ttk.Frame(master=self._topFrame)
        self._tabFrame.pack(fill=BOTH, expand=True)

        self._selected = None
        self._location = 0
        self._tabsFrame = ttk.Frame(master=self._tabFrame)
        self._tabsFrame.place(x=0, y=0, bordermode="inside")

        self._contentFrame = Frame(master=self, bd=2, relief=SUNKEN)
        self._contentFrame.pack(fill=BOTH, expand=True)

        self._contentScrollbar = Scrollbar(self._contentFrame, orient=VERTICAL)
        self._contentScrollbar.config(command=self._content_scroll)
        self._contentScrollbar.pack(fill=Y, side=RIGHT)

        self._content = Text(self._contentFrame, bd=0, wrap=WORD)
        self._content.config(yscrollcommand=self._content_scroll_bar)
        self._content.pack(fill=BOTH, expand=True)

    def _tabs_slide_reset(self):
        self._location = 0
        self._tabsFrame.place(x=self._location,y=0)

    def _tabs_slide_left(self,event):
        if self._tabsFrame.winfo_width() > self._tabFrame.winfo_width():
            tabs = self._tabs()
            loc = -self._location
            for tab in tabs:
                x = tab.winfo_x()
                y = x + tab.winfo_width()
                if y > loc:
                    self._location=-min(y, self._tabsFrame.winfo_width()- self._tabFrame.winfo_width())
                    self._tabsFrame.place(x=self._location,y=0)
                    break

    def _tabs_slide_right(self,event):
        if self._tabsFrame.winfo_width() > self._tabFrame.winfo_width():
            if self._location < 0:
                tabs = self._tabs()
                loc = -self._location
                for tab in reversed(tabs):
                    x = tab.winfo_x()
                    if x < loc:
                        self._location=-max(x,0)
                        self._tabsFrame.place(x=self._location,y=0)
                        break
    
    def _tabs_slide_to(self,tab_id):
        if self._tabsFrame.winfo_width() > self._tabFrame.winfo_width():
            tab = self._tabs_find(tab_id)
            if tab:
                start = -self._location
                end = self._tabFrame.winfo_width()-self._location
                x = tab.winfo_x()
                y = x + tab.winfo_width()
                if x < start:
                    self._location=-x
                elif y > end:
                    self._location=-y+self._tabFrame.winfo_width()
                self._tabsFrame.place(x=self._location,y=0)

    def _tabs(self):
        return self._tabsFrame.winfo_children()

    def _tabs_find(self,tab_id):
        tab = None
        tabs = self._tabs()
        if len(tabs):
            if isinstance(tab_id, Button):
                if tab_id in tabs:
                    tab = tab_id
            elif isinstance(tab_id, str):
                if tab_id == "current":
                    tab = self._selected
                elif tab_id == "first":
                    tab = tabs[0]
                elif tab_id == "last":
                    tab = tabs[-1]
            else:
                el = [x for x in tabs if x._id == tab_id]
                if len(el):
                    tab= el[0]
                elif isinstance(tab_id, int):
                    if tab_id > 0 and len(tabs) > tab_id:
                        tab = tabs[tab_id]
        return tab

    def _tabs_add(self,tab_id,**kwargs):
        tab = Button(master=self._tabsFrame,text=kwargs.pop('text', str(tab_id)), relief=GROOVE, justify=LEFT)
        tab._id = tab_id
        tab._content = kwargs.pop('content', None)
        tab.bind("<Button-1>", self._tabs_select_event)
        tab.config(cnf=TextNotebook.__config_tab_inactive)
        tab.pack(side=LEFT)
        if self._selected == None:
            self._tabs_select(tab)
        self.event_generate("<<NotebookTabAdd>>", data={"widget" : self, "id" : tab._id})

    def _tabs_remove(self,tab_id):
        tab = self._tabs_find(tab_id)
        if tab:
            self.event_generate("<<NotebookTabRemove>>", data={"widget" : self, "id" : tab._id})
            index = None
            if tab == self._selected:
                index = self._tabs().index(tab)
            tab.destroy()
            if index:
                self._tabs_select(min(index, len(self.tabs()) - 1))
    
    def _tabs_select(self,tab_id):
        tab = self._tabs_find(tab_id)
        if tab and tab != self._selected:
            if self._selected:
                self._selected.config(cnf=TextNotebook.__config_tab_inactive)
            self._selected = tab
            self._selected.config(cnf=TextNotebook.__config_tab_active)
            self._content.delete('1.0', END)
            if hasattr(tab, "_content") and tab._content:
                self._content.insert(INSERT, tab._content)
                self._content.mark_set(INSERT, '1.0')
            self._tabs_slide_to(tab_id)
            self.event_generate("<<NotebookTabChanged>>", data={"widget" : self, "id" : tab._id, "selected" : tab})

    def _tabs_select_event(self,event):
        self._tabs_select(event.widget)

    def _content_scroll(self,*args):
        self._content.yview(*args)
        self.event_generate("<<NotebookScroll>>", data={"widget" : self})

    def _content_scroll_bar(self,first,last):
        self._contentScrollbar.set(first, last)
        self.event_generate("<<NotebookScroll>>", data={"widget" : self})
    
    def content(self):
        return self._content

    def selected(self):
        return self._selected

    def index(self,tab_id):
        tab = self._tabs_find(tab_id)
        if tab:
            return self._tabs().index(tab)
        else:
            return None

    def tabs(self):
        return self._tabs()

    def tab(self, tab_id):
        return self._tabs_find(tab_id)

    def select(self,tab_id):
        self._tabs_select(tab_id)

    def add(self,tab_id,**kwargs):
        self._tabs_add(tab_id,**kwargs)

    def forget(self,tab_id):
        self._tabs_remove(tab_id)

# Test:

def _test():
    root=Tk()
    root.title("Example")
    notebook=TextNotebook(root)
    notebook.add("frame1",text="I am Tab One", content="This is some text")
    notebook.add("frame2",text="I am Tab Two", content="This is some other text")
    notebook.add("frame3",text="I am Tab Three")
    notebook.add("frame4",text="I am Tab Four")
    notebook.add("frame4",text="I am Tab Five")
    notebook.add("frame4",text="I am Tab Six")
    notebook.add("frame4",text="I Forgot How to Count")
    notebook.pack(fill="both",expand=True)
    root.mainloop()

if __name__ == '__main__':
    _test()
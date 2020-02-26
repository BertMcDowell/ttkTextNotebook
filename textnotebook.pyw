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

    CURRENT = "current"
    FIRST = 'first'
    LAST = 'last'
    END = 'end'
    ALL = 'all'

    # options
    ID = 'id'
    TEXT = 'text'
    CONTENT = 'content'
    SCROLL = 'scroll'

    def __initialize_custom_style(self):
        TextNotebook.__style = ttk.Style()
        TextNotebook.__style.configure('TextNotebook.Tabs.TFrame', background='gray69')

        TextNotebook.__config_tab_active = {
                'bg':'gray79',
                'activebackground':'gray69',
                'borderwidth':2, 
                'pady':5, 
                'padx':8, 
                'disabledforeground':'black',
                'state':DISABLED, 
                'font':'Helvetica 8 bold'
                }
        TextNotebook.__config_tab_inactive = {
                'bg':'gray69',
                'foreground':'gray24',
                'activebackground':'gray79',
                'borderwidth':1, 
                'pady':2, 
                'padx':10, 
                'disabledforeground':'black',
                'state':NORMAL, 
                'font':'Helvetica 8'
                }

    def __init__(self,master=None,*args,**kwargs):
        if not TextNotebook.__inititialized:
            self.__initialize_custom_style()
            TextNotebook.__inititialized = True

        ttk.Frame.__init__(self, master, *args)

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
        self._tabFrame.bind('<Configure>', self._tabs_configure)
        self._tabFrame.pack(fill=BOTH, expand=True)

        self._selected = None
        self._location = 0
        self._tabsCount = 0
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
            self._tabFrame.update()
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

    def _tabs_configure(self, event):
        if self._selected:
           self._tabs_slide_to(self._selected)

    def _tabs(self):
        return self._tabsFrame.winfo_children()

    def _tabs_find(self,tab_id):
        tab = None
        tabs = self._tabs()
        if len(tabs):
            if isinstance(tab_id, Button):
                if tab_id in tabs:
                    tab = tab_id
            elif isinstance(tab_id, str) and tab_id == TextNotebook.CURRENT:
                tab = self._selected
            elif isinstance(tab_id, str) and tab_id == TextNotebook.FIRST:
                tab = tabs[0]
            elif isinstance(tab_id, str) and tab_id == TextNotebook.LAST or tab_id == TextNotebook.END:
                tab = tabs[-1]
            else:
                el = [x for x in tabs if x.options[TextNotebook.ID] == tab_id]
                if len(el):
                    tab= el[0]
                elif isinstance(tab_id, int):
                    if tab_id > 0 and len(tabs) > tab_id:
                        tab = tabs[tab_id]
        return tab

    def _tabs_new(self, options):
        if TextNotebook.ID in options and TextNotebook.TEXT in options and TextNotebook.CONTENT in options and TextNotebook.SCROLL in options:
            self._tabsCount += 1
            tab = Button(master=self._tabsFrame,text=options[TextNotebook.TEXT], relief=GROOVE, justify=LEFT)
            tab.options = options
            tab.bind("<Button-1>", self._tabs_select_event)
            tab.config(cnf=TextNotebook.__config_tab_inactive)
            tab.pack(side=LEFT)
            return tab
        return None
    
    def _tabs_options(self,tab_id,**kwargs):
        tab = self._tabs_find(tab_id)
        if tab:
            option = None
            for key, value in kwargs.items():
                if value:
                    if key == TextNotebook.TEXT:
                        if isinstance(value, str):
                            tab.options[key] = value
                            tab['text'] = value
                    elif key == TextNotebook.CONTENT:
                        if isinstance(value, str):
                            tab.options[key] = value
                    elif key == TextNotebook.SCROLL:
                        print("Error scroll can not be changed")
                    else:
                        tab.options[key] = value
                else:
                    option = key

            if tab == self._selected:
                tab.options[TextNotebook.SCROLL] = self._content.yview()[0]
                if kwargs.get(TextNotebook.CONTENT):
                    self._selected = None
                    self._tabs_select(tab)

            if option:
                if option in tab.options:
                    return tab.options[option]
            else:
                return tab.options
        return None

    def _tabs_add(self,tab_id,**kwargs):
        options = { 
                TextNotebook.ID : tab_id, 
                TextNotebook.TEXT : kwargs.pop('text', str(tab_id)), 
                TextNotebook.CONTENT : kwargs.pop('content', None), 
                TextNotebook.SCROLL : 0.0 
        }
        for key, value in kwargs.items():
            options[key] = value
        tab = self._tabs_new(options)
        if self._selected == None:
            self._tabs_select(tab)
        self.event_generate("<<NotebookTabAdd>>", data={"widget" : self, "id" : tab.options[TextNotebook.ID], "tab" : tab})
        return tab

    def _tabs_remove(self,tab_id):
        if isinstance(tab_id, str) and tab_id == TextNotebook.ALL:
            tabs = self._tabs()
            for tab in tabs:
                tab.destroy()
            self._selected = None
            self._tabsCount = 0
            self._content.delete('1.0', END)
            self._tabs_slide_reset()
            self.event_generate("<<NotebookTabRemoveAll>>", data={"widget" : self})
        else:
            tab = self._tabs_find(tab_id)
            if tab:
                self.event_generate("<<NotebookTabRemove>>", data={"widget" : self, "id" : tab.options[TextNotebook.ID], "tab" : tab})
                self._tabsCount -= 1
                index = None
                if tab == self._selected:
                    index = self._tabs().index(tab)
                tab.destroy()
                if index:
                    self._selected = None
                    self._content.delete('1.0', END)
                    self._tabs_select(min(index, len(self.tabs()) - 1))
    
    def _tabs_select(self,tab_id):
        tab = self._tabs_find(tab_id)
        if tab and tab != self._selected:
            if self._selected:
                self._selected.options[TextNotebook.SCROLL] = self._content.yview()[0]
                self._selected.config(cnf=TextNotebook.__config_tab_inactive)
            self._selected = tab
            self._selected.config(cnf=TextNotebook.__config_tab_active)
            self._content.delete('1.0', END)
            if TextNotebook.CONTENT in self._selected.options and self._selected.options[TextNotebook.CONTENT]:
                self._content.insert(INSERT, self._selected.options[TextNotebook.CONTENT])
                self._content.mark_set(INSERT, '1.0')
            self._tabs_slide_to(tab_id)
            self.event_generate("<<NotebookTabChanged>>", data={"widget" : self, "id" : tab.options[TextNotebook.ID], "selected" : tab})
            try:
                self._content.yview_moveto(self._selected.options[TextNotebook.SCROLL])
                self._content.yview_moveto(self._selected.options[TextNotebook.SCROLL])
            except Exception as exception:
                print(exception)
        return self._selected

    def _tabs_select_event(self,event):
        self._tabs_select(event.widget)

    def _content_scroll(self,*args):
        self._content.yview(*args)
        self.event_generate("<<NotebookScroll>>", data={"widget" : self})

    def _content_scroll_bar(self,first,last):
        self._contentScrollbar.set(first, last)
        self.event_generate("<<NotebookScroll>>", data={"widget" : self})
    
    def dump(self):
        dump_tabs = []
        tabs = self._tabs()
        for tab in tabs:
            dump_tabs.append(self._tabs_options(tab))
        dump = {
            'tabs' : dump_tabs,
            'selected' : self.tab(self._selected, option=TextNotebook.ID)
        }
        return dump

    def restore(self, dump):
        if isinstance(dump, dict):
            if 'tabs' in dump and isinstance(dump['tabs'], list):
                self._tabs_remove(ALL)
                for options in dump['tabs']:
                    self._tabs_new(options)
            selected_tab_id = FIRST
            if 'selected' in dump and dump['selected']:
                selected_tab_id = dump['selected']
            self._tabsFrame.update()
            self._tabs_select(selected_tab_id)

    def content(self):
        return self._content

    def index(self,tab_id):
        """Returns the numeric index of the tab specified by tab_id, or
        the total number of tabs if tab_id is the string "end"."""
        if isinstance(tab_id, str) and tab_id == TextNotebook.END:
            return self._tabsCount
        else:
            tab = self._tabs_find(tab_id)
            if tab:
                return self._tabs().index(tab)
            else:
                return -1

    def select(self, tab_id=None):
        """Selects the specified tab.

        The associated child window will be displayed, and the
        previously-selected window (if different) is unmapped. If tab_id
        is omitted, returns the widget name of the currently selected
        pane."""
        return self._tabs_select(tab_id)

    def tabs(self):
        """Returns a list of windows managed by the notebook."""
        return self._tabs()

    def tab(self, tab_id, option=None, **kwargs):
        """Query or modify the options of the specific tab_id.

        If kw is not given, returns a dict of the tab option values. If option
        is specified, returns the value of that option. Otherwise, sets the
        options to the corresponding values."""
        if option is not None:
            kwargs[option] = None
        return self._tabs_options(tab_id, **kwargs)

    def add(self,tab_id,**kwargs):
        """Adds a new tab to the notebook.

        """
        return self._tabs_add(tab_id,**kwargs)

    def forget(self,tab_id):
        """Removes the tab specified by tab_id, unmaps and unmanages the
        associated window."""
        self._tabs_remove(tab_id)

# Test:

def _test():
    root=Tk()
    root.title("Example")
    notebook=TextNotebook(root)
    notebook.add("frame1",text="I am Tab One", content="This is some text")
    notebook.add("frame2",text="I am Tab Two", content="This is some other text")
    notebook.add("frame3",text="I am Tab Three", content="I am Tab Three text")
    notebook.add("frame4",text="I am Tab Four", content="I am Tab Four text")
    notebook.add("frame5",text="I am Tab Five", content="I am Tab Five text")
    notebook.add("frame6",text="I am Tab Six")
    notebook.add("frame7",text="I Forgot How to Count")
    notebook.pack(fill=BOTH,expand=True)
    root.geometry('1080x1080')
    root.mainloop()

if __name__ == '__main__':
    _test()
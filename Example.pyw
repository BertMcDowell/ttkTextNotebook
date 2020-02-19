from tkinter import *
from tkinter import ttk
from TextNotebook import *

root=Tk()
root.title("Example")
notebook=TextNotebook(root)
notebook.add("frame1",text="I am Tab One")
notebook.add("I am Tab Two")
notebook.add("I am Tab Three")
notebook.add("I Forgot How to Count")
notebook.pack(fill="both",expand=True)
root.mainloop()

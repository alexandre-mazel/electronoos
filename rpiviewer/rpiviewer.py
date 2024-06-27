from tkinter import *
from tkinter import ttk

def show_user_settings():
    root = Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
    ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=10)
    root.mainloop()
    
    
show_user_settings()
from tkinter import *
from tkinter import ttk

def show_user_settings():
    """
    from https://docs.python.org/3/library/tkinter.html
    and https://python.doctor/page-tkinter-interface-graphique-python-tutoriel
    """
    root = Tk()
    frm = ttk.Frame(root, padding=20)
    # we define a grid of 5 columns
    colcenter = 2
    frm.grid()
    nNumRow = 0
    ttk.Label(frm, text="RPIVIEWER",background="lightblue").grid(column=colcenter, row=nNumRow); nNumRow += 1
    ttk.Label(frm, text="Settings").grid(column=colcenter, row=nNumRow); nNumRow += 1
    
    radio = ttk.Checkbutton(frm,text="Nouveau?",onvalue=1,state=1)
    radio.grid(column=colcenter, row=nNumRow); nNumRow += 1
    print(radio.configure().keys())
    
    # liste
    def get_video_name():
        showinfo("Alerte", vidlist.get())

    vidlist = Listbox(root)
    vidlist.insert(1, "Vid1.mp4")
    vidlist.insert(2, "vide2.mp4")
    vidlist.insert(3, "jQuery")
    vidlist.insert(4, "CSS")
    vidlist.insert(5, "Javascript")
    vidlist.activate(2) # set focus to a specific line (seems not to work)
    vidlist.grid(column=1, row=nNumRow); nNumRow += 10
    print("sel: " + str(vidlist.curselection() ))
    
    def quit_settings():
        print("sel: " + str(vidlist.curselection() ))
        root.destroy()

        
    ttk.Button(frm, text="Quit", command=quit_settings).grid(column=colcenter, row=nNumRow)
    
    
    root.mainloop()
    
    
show_user_settings()
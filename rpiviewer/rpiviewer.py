# -*- coding: cp1252 -*-

from tkinter import *
from tkinter import ttk
import cv2

# idée: faire un rsync avec le serveur et proposé de lire des vidéos depuis le disque local ?
# on choisit en local la vidéo

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
        print("radio: " + str(radio.state() )) # alternate/selected/vide
        print("sel: " + str(vidlist.curselection() ))
        root.destroy()

    ttk.Button(frm, text="Quit", command=quit_settings).grid(column=colcenter, row=nNumRow)
    
    
    root.mainloop()
    
def sync_remote_video():
	"""
	cf https://github.com/gchamon/sysrsync
	"""
	pass

def show_video_fullscreen( filename ):
		
	print("INF: show_video_fullscreen: loading '%s'" % filename )
	import cv2
	import numpy as np
	 
	# Create a VideoCapture object and read from input file
	# If the input is the camera, pass 0 instead of the video file name
	
	print("opening...")
	cap = cv2.VideoCapture(filename)
	 
	# Check if camera opened successfully
	if (cap.isOpened()== False): 
	  print("Error opening video stream or file")
	 
	# Read until video is completed
	while(cap.isOpened()):
		# Capture frame-by-frame
		ret, frame = cap.read()
		if ret == True:

			print("displaying...")
			# Display the resulting frame
			cv2.imshow('Frame',frame)

			# Press Q on keyboard to  exit
			if cv2.waitKey(25) & 0xFF == ord('q'):
				break

			# Break the loop
			else: 
				break
	# When everything done, release the video capture object
	cap.release()
	
	
#~ show_user_settings()

show_video_fullscreen("/home/na/videos/ads_manpower.mp4")

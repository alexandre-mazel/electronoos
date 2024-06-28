# -*- coding: cp1252 -*-

from tkinter import *
from tkinter import ttk
import cv2
import os
import time

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


def ensureFps( timeStart,nNumFrame,rWantedFps ):
    """
    wait a bit to ensure a fps is keeped (the loop need to be faster as we can't wait a negative time)
    """
    
    rTheoricTime = nNumFrame / rWantedFps
    rDiff = rTheoricTime - (time.time()-timeStart)
    #~ print( "DBG: ensureFps: rDiff: %5.3fs" % rDiff )
    rMargin = 0.01
    if rDiff > rMargin:
        time.sleep(rDiff-rMargin)
    

def show_video_fullscreen( filename, bLoop = False ):
        
    print("INF: show_video_fullscreen: loading '%s'" % filename )
    import cv2
    import numpy as np
     
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name

    print( "INF: show_video_fullscreen: opening...")
    cap = cv2.VideoCapture(filename)
     
    # Check if camera opened successfully
    if (cap.isOpened()== False): 
      print("ERR: show_video_fullscreen: Error opening video stream or file")
      
    nNbrFrame = int(cap.get(cv2. CAP_PROP_FRAME_COUNT))
    rWantedFps = int(cap.get(cv2. CAP_PROP_FPS))
    nDurationFrame = int(1000./rWantedFps)
    
    print( "INF: show_video_fullscreen: rWantedFps: %5.3f, rDurationFrame: %5.3f" % (rWantedFps,nDurationFrame) )
    
    
    strWinName = "Frame"
    
    cv2.namedWindow(strWinName, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(strWinName, 1920//3, 1080//3) # set a window size in case the next property fail (eg when launched from a putty shell) // reduces as it's soo slow with my network
    cv2.setWindowProperty(strWinName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    
    nNumFrame = 0
    timeStart = time.time()
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret != True:
            if not bLoop:
                break
            else:
                # restart at begin
                print( "INF: show_video_fullscreen: looping...")
                cap.release()
                cap = cv2.VideoCapture(filename)
                ret, frame = cap.read()
                nNumFrame = 0
                timeStart = time.time()
                
        
        if 1:
            cv2.putText(frame,"%d/%d, t:%5.2fs" % (nNumFrame,nNbrFrame,time.time()-timeStart), 
                (10,30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1,
                (0x7F, 0x7F, 0x7F),
                1,
                2)

        # Display the resulting frame
        cv2.imshow(strWinName,frame)

        # Press Q on keyboard to  exit
        ch = cv2.waitKey(nDurationFrame//2) & 0xFF # le //2 is to ensure we're faster, then we'll wait a bit in ensureFps
        if  ch == ord('q') or ch == 27:
            print( "INF: show_video_fullscreen: quit received")
            break
            
                
        nNumFrame += 1
            
        ensureFps(timeStart,nNumFrame,rWantedFps)
            
        if (nNumFrame & 0x7F) == 0x7F:
            print("INF: real fps: %5.2f" % (nNumFrame/(time.time()-timeStart)) )
            



    # When everything done, release the video capture object
    cap.release()

	
#~ show_user_settings()

strLocalPath = "/home/na"

if os.name == "nt":
    strLocalPath = "c:/"

show_video_fullscreen(strLocalPath+"/videos/sdaec_farmcow.mp4", bLoop=True)

# -*- coding: cp1252 -*-

from tkinter import *
from tkinter import ttk
import cv2
import os
import sysrsync
import time

# id�e: faire un rsync avec le serveur et propos� de lire des vid�os depuis le disque local ?
# on choisit en local la vid�o

class MyCheckbox(ttk.Checkbutton):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.variable = BooleanVar(self)
        self.config(variable=self.variable)

    def isChecked(self):
        return self.variable.get()
        
    def setChecked(self,bIsChecked):
        self.variable.set(bIsChecked)

    def check(self):
        self.variable.set(True)

    def uncheck(self):
        self.variable.set(False)

if 0:

    def setCheckboxChecked(checkbox,bSelected):
        """
        change a checkbox widget, bSelected: True => checked, False => unchecked, -1 => unknown
        """
        if bSelected:
            # checkbox.state(['selected'])
            checkbox.set(True)
        elif bSelected == False:
            #~ checkbox.deselect()
            checkbox.state([])
        # else si -1: ne fait rien!
        return
        
    def getCheckboxChecked(checkbox):
        readedState = checkbox.state()
        if len(readedState)>0:
            if readedState[0] == 'alternate':
                return -1
            if readedState[0] == 'selected': # or directly:  "selected" in self.checkbutton.state()
                return True

        return False


def updateFromServer(strLocalPath):
    if os.name == "nt":
        print("WRN: updateFromServer: no rsyncing on windows")
        return
    strRemoteServer = "192.168.0.50"
    strRemotePath = '/home/na/dev/git/obo/www/agent/videod/'
    
    print( "INF: updateFromServer: sync: %s:%s => %s" % (strRemoteServer,strRemotePath,strLocalPath) )
    sysrsync.run(source=strRemotePath, destination=strLocalPath, source_ssh=strRemoteServer, options=['--size-only','--verbose', '--recursive' ], verbose = True )
    
def retrieveLocalVideos(strLocalPath):
    listFiles = os.listdir(strLocalPath)
    return listFiles

def show_user_settings(strPath, listSettings):
    """
    from https://docs.python.org/3/library/tkinter.html
    and https://python.doctor/page-tkinter-interface-graphique-python-tutoriel
    
    return settings
    """
    root = Tk()
    frm = ttk.Frame(root, padding=20)
    # we define a grid of 5 columns
    colcenter = 2
    frm.grid()
    nNumRow = 0
    ttk.Label(frm, text="RPIVIEWER",background="lightblue").grid(column=colcenter, row=nNumRow); nNumRow += 1
    ttk.Label(frm, text="Settings").grid(column=colcenter, row=nNumRow); nNumRow += 1
    
    checkbox = MyCheckbox(frm,text="Nouveau?",onvalue=1,state=1)
    checkbox.grid(column=colcenter, row=nNumRow); nNumRow += 1
    print(checkbox.configure().keys())
    
    checkbox.setChecked(listSettings[0])
    
    # liste
    def get_video_name():
        showinfo("Alerte", vidlist.get())
        
    allVideos = retrieveLocalVideos(strPath)

    vidlist = Listbox(root)
    
    for i,f in enumerate(allVideos):
        vidlist.insert(i+1, f)

    vidlist.grid(column=1, row=nNumRow); nNumRow += 10


    vidlist.selection_set(listSettings[1])
    
    def quit_settings():
        print("INF: in quit_settings...")
        print("checkbox: " + str(checkbox.state() )) # alternate/selected/vide
        print("video selected: " + str(vidlist.curselection() ))
        
        bIsSelected = checkbox.isChecked()
        
        nNumSelected = 0
        curSel = vidlist.curselection()
        if len(curSel)>0:
            nNumSelected = curSel[0]
        
        # in place storing
        listSettings[0] = bIsSelected
        listSettings[1] = nNumSelected
        listSettings[2] = allVideos[nNumSelected]
        
        root.destroy()

    ttk.Button(frm, text="Quit", command=quit_settings).grid(column=colcenter, row=nNumRow)
    
    
    root.mainloop()
    
    print("INF: show_user_settings: exiting with settings: %s" % str(listSettings))
    
    return listSettings
    
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
            
    # while is open - end
    
    cap.release()
    
# show_video_fullscreen - end

strLocalPath = "/home/na/"

if os.name == "nt":
    strLocalPath = "c:/"
    
strLocalPath += "videos/"

    
if 0:
    updateFromServer(strLocalPath)

if 1:
    listSettings = [False,0,""]
    listSettings = show_user_settings(strLocalPath,listSettings)
    show_user_settings(strLocalPath,listSettings)
    
if 1:
    #~ show_video_fullscreen(strLocalPath+"sdaec_farmcow.mp4", bLoop=True)
    show_video_fullscreen(strLocalPath+listSettings[2], bLoop=True)


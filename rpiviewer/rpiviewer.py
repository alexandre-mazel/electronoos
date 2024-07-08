# -*- coding: cp1252 -*-

"""

Raspberry Viewer for the Caves du Louvre.
v0.9
(c) A.Mazel 2024


# on RPI4, la 3D ne semble pas activé sur le raspberry.

cat /proc/device-tree/soc/firmwarekms@7e600000/status
disabled
cat /proc/device-tree/v3dbus/v3d@7ec04000/status
okay

# on Raspberry Pi 3 the v3dbus command should be:
cat /proc/device-tree/soc/v3d@7ec00000/status


Passer l'ecran en 1280x720 pour accelerer la lecture
"""

from tkinter import *
from tkinter import ttk
import cv2 # rpi: sudo apt install python3-opencv
import json
import os
import sys
import sysrsync # rpi: sudo pip install sysrsync --break-system-packages
import time

# idée: faire un rsync avec le serveur et proposé de lire des vidéos depuis le disque local ?
# on choisit en local la vidéo

import socket

def getLocalIP():   
    IP = "???"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
        s.close()    
        print("DBG: getLocalIP: " + IP)
    except:
        pass
    return IP

def setMousePos(x,y):
    if os.name == "nt":
        import win32api
        win32api.SetCursorPos((x,y))
    else:        
        import pyautogui #  sudo pip install pyautogui --break-system-packages
        pyautogui.moveTo(x, y, duration = 1) # doesn't seem to work
        """
        from Xlib import X, display
        d = display.Display()
        s = d.screen()
        root = s.root
        root.warp_pointer(300,300)
        d.sync()
        """

def turnPC_ScreenOn(bIsOn):
    """
    Function to turn on or off the PC screen.
    bIsOn: True => on, False => off
    """
    print("INF: turnPC_ScreenOn: %s" % bIsOn )
    if os.name == "nt":
        import win32gui
        import win32con
        nNewState = 2
        if bIsOn:
            nNewState = -1
        win32gui.SendMessage(win32con.HWND_BROADCAST, win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, nNewState)
        if 0:
            # quite the same:
            import ctypes
            ctypes.windll.user32.SendMessageW(65535, 274, 61808,nNewState)
        return
    # linux / rpi

def handleInput():
    """
    Fonction dans le cas ou on redirige la sortie de l'executable cec dans notre programme (mais en fait avec la lib cec c'est plus propre) cf handleCecCommand
    """
    if 0:
        #buf = sys.stdin.readlines()
        buf = sys.stdin.read()
        print( "INF: handleInput: buf: " + str(buf) )
    if 0:
        import fileinput
        for line in fileinput.input():
            print( "INF: handleInput: line: " + str(line) )
            
    if 1:
        # check data
        if os.name == "nt":
            import msvcrt
            if not msvcrt.kbhit(): 
                return
        else:
            import select
            if not select.select([sys.stdin, ], [], [], 0.0)[0]:
                return
            
        for line in sys.stdin:
            print(f'Input : {line}')
            break
        print("exiting...")
    
    
def loopHandleInput():
    print( "INF: loopHandleInput: looping...")
    while 1:
        handleInput()
        print(".")
        time.sleep(0.5)
        
def keyPressCallback(key,duration):
    return 0
    print("[key pressed] " + str(key))
    if key == 0:
        startUserSettings()
    return 0
    
def LogCallback(s):
    print("DBG: LogCallback: " + str(s) )
        
def handleCecCommand():
    print( "INF: handleCecCommand...")
    
    import cec # sudo apt-get install libcec-dev python3-cec
    
    #~ adapters = cec.list_adapters() # may be called before init()

    #~ cec.init() # use default adapter
    #~ cec.init(adapter) # use a specific adapter
    
    cecconfig = cec.libcec_configuration()
    cecconfig.strDeviceName = "libCEC"
    cecconfig.bActivateSource = 1
    cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
    cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
    #~ cecconfig.SetLogCallback(LogCallback)
    cecconfig.SetKeyPressCallback(keyPressCallback) # quand on active cette ligne ca fait un coredump plus tard
    
    lib = cec.ICECAdapter.Create(cecconfig)
    detected = lib.DetectAdapters()
    print("detected: %s" % str(detected) )
    print("detected0: %s" % dir(detected[0]) )
    print("detected0.strComPath: %s" % str(detected[0].strComPath) )
    print("detected0.strComName: %s" % str(detected[0].strComName) )
    print("detected0.iProductId: %s" % str(detected[0].iProductId) )
    print("detected0.iVendorId: %s" % str(detected[0].iVendorId) )
    print("detected1: %s" % str(detected[1].strComName) )
    adapter = detected[0].strComName
    print("INF: handleCecCommand: Opening...")
    lib.Open(adapter)
    print("INF: handleCecCommand: Open")
    return lib
    
   
def cb_CecAlt(event, *args):
    evKeyPress = 2
    kOK = 0
    kUp = 1
    kDown = 2
    kLeft = 3
    kRight = 4
    global global_bShowSettings
    global root    
    print("DBG: cb_CecAlt: Got event", event, "with data", args)
    if event == evKeyPress:
        print("INF: cb_CecAlt: got keypress")
        key, down = args
        if down == 0:
            if key == kOK:
                #~ startUserSettings()
                print("INF: cb_CecAlt: Ok received")
                if not global_bShowSettings:
                    global_bShowSettings = True
                else:
                    global_bShowSettings = False
                    root.event_generate("<<Quit>>")
            if key == kDown:
                print("INF: cb_CecAlt: DOWN!")
                root.event_generate("<<Down>>")
            if key == kUp:
                print("INF: cb_CecAlt: UP!")
                root.event_generate("<<Up>>")

    
def handleCecCommandAlt():
    # from https://github.com/trainman419/python-cec
    # git clone https://github.com/trainman419/python-cec
    # cd python-cec
    # make
    # cp build/lib.linux-aarch64-cpython-311/cec.cpython-311-arm-linux-gnueabihf.so ~/dev/git/electronoos/rpiviewer/
    
    sys.path.insert(0,"/home/na/dev/git/python-cec/")
    # or:
    # cp ~/dev/git/python-cec/cec.cpython-311-arm-linux-gnueabihf.so  .
    try:
        import cec
    except ModuleNotFoundError as err:
        print("WRN: handleCecCommandAlt: while loading cec, err: %s" % err )
        return
        
    adapters = cec.list_adapters()
    
    print(adapters)

    if len(adapters) < 1:
        print("INF: handleCecCommandAlt: no adapters...")
        return
    
    adapter = adapters[0]
    print("Using Adapter %s"%(adapter))
    cec.init(adapter)

    print("Devices:", cec.list_devices())

    d = cec.Device(0)

    # print fields
    print("Address:", d.address)
    print("Physical Address:", d.physical_address)
    print("Vendor ID:", d.vendor)
    print("OSD:", d.osd_string)
    print("CEC Version:", d.cec_version )

    print("Installing callback...")
    cec.add_callback(cb_CecAlt, cec.EVENT_ALL & ~cec.EVENT_LOG)
    
    if 0:
        print("Creating Device object for TV")
        tv = cec.Device(0)
        print("Turning on TV")
        tv.power_on()

        print("Volume Up")
        cec.volume_up()
        #~ print("Volume Down")
        #~ cec.volume_down()
    


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
    print("INF: updateFromServer: starting...")
    if os.name == "nt":
        print("WRN: updateFromServer: no rsyncing on windows")
        return

    if getLocalIP()[:3] == "192":
        print("WRN: updateFromServer: no rsyncing on candiotti network")
        return
        
    strRemoteServer = "pi@10.0.189.248"
    strRemotePath = '/home/pi/shared/'
    try:
        sysrsync.run(source=strRemotePath, destination=strLocalPath, source_ssh=strRemoteServer, options=['-rv','--size-only','--stats'])
    except BaseException as err:
        print("ERR: updateFromServer: rsync failed, err: %s" % err )
            
    print("INF: updateFromServer: finished")
        
def retrieveLocalVideos(strLocalPath):
    listFiles = os.listdir(strLocalPath)
    return listFiles

root = Tk()
    
def show_user_settings(strPath, listSettings):
    """
    from https://docs.python.org/3/library/tkinter.html
    and https://python.doctor/page-tkinter-interface-graphique-python-tutoriel
    
    return settings
    """
    # root = Tk()
    global root
    frm = ttk.Frame(root, padding=20)
    frm.pack(fill=BOTH,expand=True)
    # we define a grid of 5 columns
    colcenter = 2
    frm.grid()
    nNumRow = 0
    ttk.Label(frm, text="RPIVIEWER by AlmaTools",background="lightblue").grid(column=colcenter, row=nNumRow); nNumRow += 1
    ttk.Label(frm, text="Settings").grid(column=colcenter, row=nNumRow); nNumRow += 1
    ttk.Label(frm, text="IP: " + getLocalIP() ).grid(column=colcenter, row=nNumRow); nNumRow += 1
    
    checkbox = MyCheckbox(frm,text="Nouveau?",onvalue=1,state=1)
    checkbox.grid(column=colcenter, row=nNumRow); nNumRow += 1
    print(checkbox.configure().keys())
    
    checkbox.setChecked(listSettings[0])
    
    # liste
    def get_video_name():
        showinfo("Alerte", vidlist.get())
        
    allVideos = retrieveLocalVideos(strPath)

    vidlist = Listbox(root,selectmode="browse",width=70,height=30) # 100,40 if hd, 70, 30 else
    
    for i,f in enumerate(allVideos):
        vidlist.insert(i+1, f)

    vidlist.grid(column=1, row=nNumRow); nNumRow += 10


    vidlist.selection_set(listSettings[1])
    
        
    def getCurrentVideoSelected():
        nNumSelected = 0
        curSel = vidlist.curselection() # currentItem() ?
        if len(curSel)>0:
            nNumSelected = curSel[0]
        return nNumSelected
    
    def quit_settings(event=None):
        global global_bShowSettings
        print("INF: in quit_settings...")
        print("checkbox: " + str(checkbox.state() )) # alternate/selected/vide
        print("video selected: " + str(vidlist.curselection() ))
        
        bIsSelected = checkbox.isChecked()
        
        nNumSelected = getCurrentVideoSelected()
        
        # in place storing
        listSettings[0] = bIsSelected
        listSettings[1] = nNumSelected
        listSettings[2] = allVideos[nNumSelected]
        
        saveSettingsToDisk(listSettings)
        
        root.destroy()
        global_bShowSettings = False
        


    def moveSelelection(nStep=1):
        print("DBG: moveSelelection: entering with step %s" % nStep )
        nNumSelected = getCurrentVideoSelected()
        #~ vidlist.selection_unset(nNumSelected)
        nNumSelected = (nNumSelected + nStep) % len(allVideos)
        print("DBG: rootDown: nNumSelected: %s" % nNumSelected )
        #vidlist.clearSelection()
        vidlist.selection_clear(0,"end")
        vidlist.selection_set(nNumSelected)
        
    def rootDown(event):
        print("DBG: rootDown: entering" )
        moveSelelection(+1)
    
    def rootUp(event):
        moveSelelection(-1)
        

    ttk.Button(frm, text="Quit", command=quit_settings).grid(column=colcenter, row=nNumRow)
    
    #~ frm.bind("<<Down>>",rootDown)
    root.bind("<<Up>>",rootUp)
    root.bind("<<Down>>",rootDown)
    root.bind("<<Quit>>",quit_settings)
    root.mainloop()
    
    root = Tk() # clean root and prepare for next call
    
    print("INF: show_user_settings: exiting with settings: %s" % str(listSettings))
    
    return listSettings
# show_user_settings - end    



    
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
    #print( "DBG: ensureFps: rDiff: %5.3fs" % rDiff )
    rMargin = 0.01
    if rDiff > rMargin:
        rTimeSleepSec = rDiff-rMargin
        print( "DBG: ensureFps: sleeping: %5.3fs" % rTimeSleepSec )
        time.sleep(rTimeSleepSec)
    


def show_video_fullscreen( filename, bLoop = False, bPrintPlayInfo = True ):
        
    print("INF: show_video_fullscreen: loading '%s'" % filename )
    global global_bShowSettings
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
    
    cv2.destroyAllWindows() # erase the prev video before creating anew, else it's not full screen
    
    cv2.namedWindow(strWinName, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(strWinName, 1920//3, 1080//3) # set a window size in case the next property fail (eg when launched from a putty shell) // reduces as it's soo slow with my network
    cv2.setWindowProperty(strWinName, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    
    nNumFrame = 0
    timeStart = time.time()
    
    nReturnCode = 0
    
    if 1:
        # move mouse top right
        _,_,w,h = cv2.getWindowImageRect(strWinName)
        setMousePos( w, 0 )
        
        
    global bRightButtonClicked # je ne comprend pas pourquoi sans cette commande, il crois que le bRightButtonClicked dans la boucle est local
    bRightButtonClicked = False
    def cb_cv2_MouseEvent(event,x,y,flags,param):
        global bRightButtonClicked
        #~ print( "INF: cb_cv2_MouseEvent: event: %s, x: %s, y: %s, flags: 0x%x, param: %s" % (event,x,y,flags,str(param)) )
        if event == cv2.EVENT_LBUTTONDOWN or event == cv2.EVENT_RBUTTONDOWN:
            print( "INF: cb_cv2_MouseEvent: Click !" )
            bRightButtonClicked = True
            print( "INF: cb_cv2_MouseEvent: bRightButtonClicked: %s" % bRightButtonClicked )

    cv2.setMouseCallback( strWinName, cb_cv2_MouseEvent )
    
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
                
        
        if bPrintPlayInfo and 0:
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
        ch = cv2.waitKey(nDurationFrame//10) & 0xFF # le //2 is to ensure we're faster, then we'll wait a bit in ensureFps
        if  ch == ord('q') or ch == 27:
            print( "INF: show_video_fullscreen: quit received")
            nReturnCode = 2
            break
            
        #~ print(bRightButtonClicked)
            
        if ch == 13 or bRightButtonClicked:
            print( "INF: show_video_fullscreen: show settings!")
            global_bShowSettings = True
            
        if global_bShowSettings:
            break
                
        nNumFrame += 1
            
        ensureFps(timeStart,nNumFrame,rWantedFps)
            
        if (nNumFrame & 0x7F) == 0x7F:
            print("INF: real fps: %5.2f" % (nNumFrame/(time.time()-timeStart)) )
            
    # while is open - end
    
    cap.release()
    
    # cv2.destroyAllWindows() # doing it here, hide the stucked video
    
    return nReturnCode
    
# show_video_fullscreen - end

strLocalPath = "/home/na/"

if os.name == "nt":
    strLocalPath = "c:/"
    
strLocalPath += "videos/"


global_filename_settings = "rpiviewer.dat"
def loadSettingsFromDisk(listSettings):
    try:
        f = open(global_filename_settings,"rt")
    except:
        print("WRN: loadSettingsFromDisk: no settings found")
        return listSettings 
    loadedSettings = json.load(f)
    f.close()
    if len(loadedSettings) > 0:
        print("INF: loadSettingsFromDisk: loaded %s setting(s)" % len(loadedSettings) )
        listSettings = loadedSettings
    return listSettings
    
def saveSettingsToDisk(listSettings):
    try:
        f = open(global_filename_settings,"wt")
    except:
        print("ERR: saveSettingsToDisk: save settings impossible")
        return False
        
    ret = json.dump((listSettings),f,indent=2)
    f.close()
    print("ERR: saveSettingsToDisk: saved success")
    return ret

def appLoop(strLocalPath):
    print("INF: appLoop: starting...")
    listSettings = [False,0,""]
    listSettings = loadSettingsFromDisk(listSettings)
    #~ updateFromServer(strLocalPath)
    allVideos = retrieveLocalVideos(strLocalPath)
    handleCecCommandAlt()
    if 0:
        listSettings = show_user_settings(strLocalPath,listSettings)
    
    while 1:
        strVideoFilename = allVideos[listSettings[1]]
        nRet = show_video_fullscreen(strLocalPath+strVideoFilename, bLoop=True)
        if nRet == 2:
            break
        if global_bShowSettings:
            updateFromServer(strLocalPath)
            allVideos = retrieveLocalVideos(strLocalPath)
            listSettings = show_user_settings(strLocalPath,listSettings)


#~ def startUserSettings():
    #~ print("INF: startUserSettings" )
    #~ global global_listSettings, strLocalPath
    #~ global_listSettings = show_user_settings(strLocalPath,global_listSettings)

global_listSettings = [False,0,""]
global_bShowSettings = False


if 0:
    global_listSettings = show_user_settings(strLocalPath,global_listSettings)
    show_user_settings(strLocalPath,global_listSettings)
    
if 0:
    #~ show_video_fullscreen(strLocalPath+"sdaec_farmcow.mp4", bLoop=True)
    global_listSettings = loadSettingsFromDisk(global_listSettings)
    show_video_fullscreen(strLocalPath+global_listSettings[2], bLoop=True)
    exit(1)
    
if 0:
    updateFromServer(strLocalPath)
    exit(1)
    
if 1:
    turnPC_ScreenOn(0) # le probleme c'est que sur mon portable mstab7, ca gele l'ordi, et donc les lignes suivantes ne sont pas éxécutées...
    time.sleep(10)
    turnPC_ScreenOn(1)
    exit(1)
    
if 0:
    #~ loopHandleInput()
    #~ cecobj = handleCecCommand()
    cecobj = handleCecCommandAlt()
    while 1:
        print(".")
        if global_bShowSettings:
            global_bShowSettings = False
            global_listSettings = show_user_settings(strLocalPath,global_listSettings)
            
        time.sleep(1.)
        
        #~ if 1:
            #~ cb_CecAlt(2,0,0)
            
appLoop(strLocalPath)
    



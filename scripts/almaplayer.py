import sys
import os
import msvcrt
import pygame as pg
import time

sys.path.append("../alex_pytools/")
sys.path.append("C:/Users/alexa/dev/git/electronoos/alex_pytools/")
import sound_player

timeLastNext = time.time()-100

def playSongInterruptible(strFilename):
    """
    return -1 on error, 0 if finished, 1 if skipped, 2 if want to exit
    """
    print("INF: playing '%s'" % strFilename )
    global timeLastNext
    try:
        sound_player.playFile(strFilename,bWaitEnd=False)
    except BaseException as err:
        print("ERR: song not playable: %s (err: %s)" % (strFilename,err))
        return -1
        
    print("press n to next of up and down for vol up and vol down")
    while pg.mixer.music.get_busy():
        #~ pg.time.Clock().tick(1) #too long => block to 1fps
        #~ time.sleep(0.1)
        pg.time.Clock().tick(100) 
        if msvcrt.kbhit():
            pressedKey = msvcrt.getch()
            print("pressedKey: %s" % (pressedKey))
            if pressedKey == b'\xe0':
                print("arrow")
                pass
            if pressedKey == b'\x1b':
                print("esc")
                return 2
            else:
                try:
                    # decode key as char
                    key = pressedKey.decode()
                    print("key: %s" % key )
                    if key == 'n':
                        print("skipping current song...")
                        if time.time()-timeLastNext > 3: # we dont want to fade if in a rapid series of next
                            print("fading...")
                            timeLastNext = time.time()
                            pg.mixer.music.fadeout(1000)
                            time.sleep(1) #fadout is not blocking
                        pg.mixer.music.stop()
                        return 1
                    if key == 'H':
                        print("vol up")
                        pg.mixer.music.set_volume(pg.mixer.music.get_volume()+0.1)
                        print("new vol: %s" % pg.mixer.music.get_volume())
                    if key == 'P':
                        print("vol down")
                        pg.mixer.music.set_volume(pg.mixer.music.get_volume()-0.1)
                        print("new vol: %s" % pg.mixer.music.get_volume())
                except BaseException as err:
                    print("ERR: playSongInterruptible: catched %s" % err )
    return 0


def playAllFileFromFolder( strPath, listToExclude=[], strStartFrom = "" ):
    """
    - strStartFrom: if set it will start with this song
    """
    bSearchStart = strStartFrom != ""
    
    listFiles = sorted(os.listdir(strPath))
    for f in listFiles:
        if ".mp3" not in f and ".mp4" not in f :
            continue
        if bSearchStart:
            if f != strStartFrom:
                continue
            # else, it's the one to start!
            bSearchStart = False
        
        if listToExclude != [] and f in listToExclude:
            continue
        print("Playing '%s'" % f)
        absf = strPath + f
        if(playSongInterruptible(absf)==2):
            return
    #~ input("press a key")
    

if __name__ == "__main__":
    try:
        #print(sys.argv)
        if len(sys.argv)>1:
            mp3file = sys.argv[1]
            if playSongInterruptible(mp3file) != 2:
                # trouve les autre chansons du dossier et les joue (mais que les suivantes)
                strPath, strFilename = os.path.split(mp3file)
                playAllFileFromFolder(strPath+os.sep, [strFilename],strStartFrom=strFilename)
             
    except BaseException as err:
        print("ERR: Almaplayer, catched error: %s" % str(err))
        input("press a key")
        exit(-1)
exit(0)
    
    
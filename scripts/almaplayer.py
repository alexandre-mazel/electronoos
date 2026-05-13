import sys
import os
import msvcrt
import pygame as pg
import time
"""
Exemple a essayer pour communiquer avec un popen:

from subprocess import Popen, PIPE

pipes = dict(stdin=PIPE, stdout=PIPE, stderr=PIPE)
mplayer = Popen(["mplayer", "asdf.m4a"], **pipes)

# to control u can use Popen.communicate
mplayer.communicate(input=b">")
sys.stdout.flush()
"""


sys.path.append("../alex_pytools/")
sys.path.append("C:/Users/alexa/dev/git/electronoos/alex_pytools/")
import sound_player
import misctools

timeLastNext = time.time()-100

def playM4a(strFilename):
    ret = os.system('C:\\Progra~2\\VideoLAN\\VLC\\vlc.exe --play-and-exit "%s"' % strFilename)
    print(dir(os))
    return ret
    
def playWebm(strFilename):
    print("INF: playWebm: starting... (select unselect with mouse to enable keyboard sending)")
    import pyglet
    media = pyglet.media.load(strFilename)
    player = media.play()
    #~ print(dir(player))
    bInPause = False
    while 1:
        pyglet.clock.tick(100)
        time.sleep(0.5)
        print("\r%5.2fs / %5.2fs" % (float(player.time),float(media.duration)), end = "" )
        pyglet.clock.tick(100)
        if player.time > media.duration + 0.8: # how much did we leave ?
            print("\nSong seems finished...")
            break # or return 1?
            
        if msvcrt.kbhit():
            pressedKey = msvcrt.getch()
            print("pressedKey: %s" % (pressedKey))
            if pressedKey == b'\xe0':
                print("arrow")
                pass
            elif pressedKey == b'\x1b':
                print("esc")
                player.pause()
                return 10
            else:
                key = pressedKey.decode()
                print("key: %s" % key )
                if key == 'H':
                    print("vol up")
                    player.volume(100) # ou entre 0 et 1 ?
                if key == 'p':
                    if not bInPause:
                        print("pause song")
                        player.pause()
                        bInPause = True
                    else:
                        print("resume song")
                        player.play()
                        bInPause = False
                if key == 'n':
                    player.pause()
                    return 1
                if key == 'b':
                    player.pause()
                    return 2
                if key == 'M':
                    player.seek(player.time+5.)
                if key == 'K':
                    player.seek(max(player.time-5.,0))
                    
                # todo tester player.volume(0..1)
    return True

def playSongInterruptible(strFilename):
    """
    return -1 on error, 0 if finished, 1 if skipped, 2 for prev, 10 if want to exit
    20 => shuffle the list
    """
    print("INF: playing '%s'" % strFilename )
    if ".m4a" in strFilename:
        return playM4a(strFilename)
        
    if ".webm" in strFilename or ".ogg" in strFilename:
        return playWebm(strFilename)
        
    global timeLastNext
    try:
        ret = sound_player.playFile(strFilename,bWaitEnd=False)
        print("DBG: playSongInterruptible: ret: %s" % ret )
        if ret == False:
            return -1
        #~ print("INF: playSongInterruptible: len: %s" % pg.mixer.Sounds().get_length() )
        
    except BaseException as err:
        print("ERR: playSongInterruptible: song not playable: %s (err: %s)" % (strFilename,err))
        return -1
        
    print("press n to next of up and down for vol up and vol down")
    bInPause = False
    while pg.mixer.music.get_busy() or bInPause:
        #~ pg.time.Clock().tick(1) #too long => block to 1fps
        #~ time.sleep(0.1)
        pg.time.Clock().tick(100) 
        
        # spectrum analysis
        if 0:
            import numpy as np
            raw_data = pg.mixer.music.get_raw()
            audio_array = np.frombuffer(raw_data, dtype=np.int16)
            max = np.max(audio_array)
            print(max)
            #~ spectrum = np.fft.fft(audio_array)
            
        if msvcrt.kbhit():
            pressedKey = msvcrt.getch()
            print("pressedKey: %s" % (pressedKey))
            if pressedKey == b'\xe0':
                print("arrow")
                pass
            if pressedKey == b'\x1b':
                print("esc")
                return 10
            else:
                try:
                    # decode key as char
                    key = pressedKey.decode()
                    print("key: %s" % key )
                    if key == 's':
                        print("stopping current song...")
                        print("fading...")
                        timeLastNext = time.time()
                        pg.mixer.music.fadeout(1500)
                        time.sleep(1.5) #fadout is not blocking
                        pg.mixer.music.stop()
                        return 10
                    if key == 'r':
                        print("stopping current song and randomizing the list...")
                        print("fading...")
                        timeLastNext = time.time()
                        pg.mixer.music.fadeout(1500)
                        time.sleep(1.5) #fadout is not blocking
                        pg.mixer.music.stop()
                        return 20
                    if key == 'n':
                        print("skipping current song...")
                        if time.time()-timeLastNext > 3: # we dont want to fade if in a rapid series of next
                            print("fading...")
                            timeLastNext = time.time()
                            pg.mixer.music.fadeout(1000)
                            time.sleep(1) #fadout is not blocking
                        pg.mixer.music.stop()
                        return 1
                    if key == 'b':
                        print("goto prev song...")
                        if time.time()-timeLastNext > 3: # we dont want to fade if in a rapid series of next
                            print("fading...")
                            timeLastNext = time.time()
                            pg.mixer.music.fadeout(1000)
                            time.sleep(1) #fadout is not blocking
                        pg.mixer.music.stop()
                        return 2
                    if key == 'p':
                        if not bInPause:
                            print("pause song")
                            pg.mixer.music.pause()
                            bInPause = True
                        else:
                            print("resume song")
                            pg.mixer.music.unpause()
                            bInPause = False
                    if key == 'H':
                        print("vol up")
                        pg.mixer.music.set_volume(pg.mixer.music.get_volume()+0.1)
                        print("new vol: %s" % pg.mixer.music.get_volume())
                    if key == 'P':
                        print("vol down")
                        pg.mixer.music.set_volume(pg.mixer.music.get_volume()-0.1)
                        print("new vol: %s" % pg.mixer.music.get_volume())
                    if key == 'M':
                        print("advance")
                        #pg.mixer.music.set_pos(pg.mixer.music.get_pos()+3000) # force skip ?
                        print("new pos: %s" % pg.mixer.music.get_pos())
                except BaseException as err:
                    print("ERR: playSongInterruptible: catched %s" % err )
    return 0


def playAllFileFromFolder( strPath, listToExclude=[], strStartFrom = "" ):
    """
    - strStartFrom: if set it will start with this song
    """
    bSearchStart = strStartFrom != ""
    
    listFiles = sorted(os.listdir(strPath))
    listMusics = []
    
    print( "DBG: playAllFileFromFolder: strPath: %s" % strPath )

    for f in listFiles:
        if ".mp3" not in f and ".mp4" not in f and ".m4a" not in f and ".ogg" not in f and ".webm" not in f :
            continue
        if bSearchStart:
            if f != strStartFrom:
                continue
                
            # else, it's the one to start!
            bSearchStart = False
        
        if listToExclude != [] and f in listToExclude:
            continue
            
        listMusics.append(f)
        
    print( "INF: playAllFileFromFolder: %d songs next to play"%len(listMusics))
    n = 0
    while n < len(listMusics):
        f = listMusics[n]
        print("Playing %d: '%s'" % (n,f))
        absf = strPath + f
        ret = playSongInterruptible(absf)
        print( "DBG: playAllFileFromFolder: ret: %d" % ret )
        if ret == 10:
            return
        if ret == 20:
            print("Shuffling the list. List[5] was: %s" % str(listMusics[:5]) )
            print("WRN: Was shuffled only from the one started first")
            listMusics = misctools.shuffle(listMusics,len(listMusics))
            print("Now List[5] is: %s" % str(listMusics[:5]) )
            n = 0
        elif ret == 2:
            n -= 1
            if n < 0:
                n = len(listMusics)-1
        elif ret == -1:
            # music not playable
            print( "DBG: playAllFileFromFolder: removing song from playlist..." )
            del listMusics[n]
            if n >= len(listMusics):
                n = len(listMusics)-1
            print( "DBG: playAllFileFromFolder: removing song from playlist, now n:%d and len: %d" % (n,len(listMusics) ))
        else:
            n += 1
        #~ input("press a key")
        
    

if __name__ == "__main__":
    try:
        #print(sys.argv)
        if len(sys.argv)>1:
            mp3file = sys.argv[1]
            if 0:
                # ancienne facon (probleme c'est que la premiere fois, les touches comme r ne sont pas geres)
                if playSongInterruptible(mp3file) != 10:
                    # trouve les autre chansons du dossier et les joue (mais que les suivantes)
                    strPath, strFilename = os.path.split(mp3file)
                    if os.sep not in mp3file:
                        strPath = "."+os.sep
                    playAllFileFromFolder( strPath+os.sep, [strFilename],strStartFrom=strFilename )
            else:
                strPath, strFilename = os.path.split(mp3file)
                if os.sep not in mp3file:
                    strPath = "."+os.sep
                playAllFileFromFolder( strPath+os.sep, [],strStartFrom=strFilename )
                
             
    except BaseException as err:
        print("ERR: Almaplayer, catched error: %s" % str(err))
        #input("press a key")
        exit(-1)
exit(0)
    
    
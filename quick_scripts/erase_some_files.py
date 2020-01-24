

# when too much files in a folder (>500000), the system command fail to erase *.*, it says: "rm cannot remove '*.*': No such file or directory", same for ls
# or -bash: /bin/ls: Argument list too long
# (on Nano 18.04)

import os
import shutil

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

def deleteFile( strPath, mask_part_of_file ):
    """
    mask: file containing this string will be deleted, eg: ".jpg, or "2020-01-09" ...
    """
    print("INF: deleteFile in %s matching %s..." % (strPath, mask_part_of_file) )    
    listFile = os.listdir(strPath)
    listToDel = []
    
    for f in listFile:
        if mask_part_of_file in f:
            filename = strPath + os.sep + f
            listToDel.append(filename)
            
    print("\nWRN: really erase %d files ?\n\n they looks like: %s... ...\n(press y)" % (len(listToDel), "\n".join(listToDel[:10]) ) )
    
    ch = getch()
    if ch == 'y':
        print("INF: Processing...")
        for f in listToDel:
            os.remove(f)


deleteFile( "/var/www/html/data", "2020_01_08" )
# -*- coding: cp1252 -*-

import json
import time
import win32gui
import pywintypes



import sys
sys.path.append("../alex_pytools/")
import misctools

def replaceNameReplaceByNonAccentuatedChars(s):
    trans = [
                    # ne pas mettre d'underscore ici
                    ( "\\N{LATIN CAPITAL LETTER E WITH ACUTE}", "E" ),
                    ( "\\N{LATIN CAPITAL LETTER E WITH GRAVE}", "E" ),
                    ( "\\N{LATIN CAPITAL LETTER E WITH CIRCUMFLEX}", "E" ),
                    ( "\\N{LATIN SMALL LETTER A WITH CIRCUMFLEX}", "a" ),
                    ( "\\N{LATIN SMALL LETTER A WITH ACUTE}", "a" ),
                    ( "\\N{LATIN SMALL LETTER A WITH GRAVE}", "a" ),
                    ( "\\N{LATIN SMALL LETTER C WITH CEDILLA}", "c" ),
                    ( "\\N{LATIN SMALL LETTER E WITH ACUTE}", "e" ),
                    ( "\\N{LATIN SMALL LETTER E WITH DIAERESIS}", "e" ),
                    ( "\\N{COMBINING ACUTE ACCENT}", "e" ),
                    ( "\\N{LATIN SMALL LETTER E WITH GRAVE}", "e" ),
                    ( "\\N{LATIN SMALL LETTER I WITH CIRCUMFLEX}", "i" ),
                    ( "\\N{LATIN SMALL LETTER N WITH TILDE}", "n" ),
                    ( "\\N{LATIN SMALL LETTER O WITH CIRCUMFLEX}", "o" ),
                    ( "\\N{LATIN SMALL LETTER O WITH DIAERESIS}", "o" ),
                    ( "\\N{LATIN CAPITAL LETTER O WITH STROKE}", "O" ),
                    ( "\\N{LEFT SINGLE QUOTATION MARK}", "'" ),
                    ( "\\N{RIGHT SINGLE QUOTATION MARK}", "'" ),
                    ( "\\N{FULLWIDTH QUOTATION MARK}", "'" ),
                    ( "\\N{ACUTE ACCENT}", "'" ),
                    ( "\\N{LEFT-POINTING DOUBLE ANGLE QUOTATION MARK}", '"' ),
                    ( "\\N{RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK}", '"' ),
                    ( "\\N{FULLWIDTH COLON}", ':' ),
                    ( "\\N{FULLWIDTH QUESTION MARK}", '?' ),
                    ( "\\N{LEFT DOUBLE QUOTATION MARK}", '?' ),
                    ( "\\N{RIGHT DOUBLE QUOTATION MARK}", '?' ),
                    ( "\\N{NO-BREAK SPACE}", " " ),
                    ( "\\N{ZERO WIDTH SPACE}", " " ),
                    ( "\\N{EM DASH}", "-" ),
                    ( "\\N{EN DASH}", "-" ),
                    ( "\\N{FULLWIDTH VERTICAL LINE}", "-" ),
                    ( "\\N{BULLET}", "o" ),
                    ( "\\N{DEGREE SIGN}", "o" ),
                    ( "\\N{FLEXED BICEPS}", "" ),
                    ( "\\N{BLACK RIGHT-POINTING POINTER}", "-" ),
                    ( "\\N{BLACK LEFT-POINTING POINTER}", "-" ),
                    ( "\\N{FIREWORKS}", "-" ),
                    ( "\\N{BIG SOLIDUS}", "-" ),
                    ( "\\N{BIG REVERSE SOLIDUS}", "-" ), # c'est cense etre l'anti slash, mais on met juste un -
                    
                    ( "\\N{HANGUL SYLLABLE HAE}", "X" ), # caractere coréen qui veut dire spring
                    ( "\\N{HANGUL SYLLABLE SEOG}", "X" ), # qui veut dire night (ou l'inverse) #faire un code qui change tout les HANGUL_SYLLABLE_* par rien ou X
                    
                    
                    
                ]
    for a,b in trans:
        s = s.replace(a,b)
    return s
    
def cleanTitle( strTitle ):
    while " - pupu" in strTitle:
        strTitle = strTitle.replace( " - pupu", "" )
    for strAtEnd in [ "- pup", "- pu", "- p" ]:
        if strTitle[-len(strAtEnd):] == strAtEnd:
            strTitle = strTitle[:-len(strAtEnd)]
    while "  " in strTitle:
        strTitle = strTitle.replace( "  ", " " )
    strTitle = strTitle.strip()
    return strTitle


def getParentWindow( hWnd ):
    """
    return None if no parent
    """
    try:
        hParent = win32gui.GetParent(hWnd)
        if hParent == None or hParent == win32gui.GetDesktopWindow():
            return None
        return hParent
    except (BaseException, pywintypes.error) as err:
        return None
    
def getParentName( hWnd ):
    hParent = getParentWindow(hWnd)
    if hParent == None:
        return ""
    title = win32gui.GetWindowText( hParent )
    return title

def getCurrentWindowTitleName():
    
    hCurrentWindow = win32gui.GetForegroundWindow()
    if hCurrentWindow == None:
        return ""
    title = win32gui.GetWindowText( hCurrentWindow )
    titleParent = getParentName( hCurrentWindow )
    if titleParent != "":
        title += " // " + titleParent
    return title
    
    
    
class Statis3:
    def __init__ ( self ):
        self.strSaveFilename = "c:\\save\\statis3.dat"
        self.dAllTitle = {} # for each title, the time in sec
        self.load()
        
    def __del__(self):
        print("DBG: Statis3.del...")
        #~ self.save() # ca pete tout!
        
    def save( self ):
        print("DBG: Statis3.save: saving to '%s'" % str(self.strSaveFilename))
        misctools.backupFile(self.strSaveFilename)
        f = open(self.strSaveFilename,"wt")
        ret = json.dump((self.dAllTitle),f,indent=2,ensure_ascii =False)
        f.close()
        #~ self.loadedTime = time.time()+0.0001
        
    def load( self ):
        try:
            f = open(self.strSaveFilename,"rt")
        except FileNotFoundError:
            print("WRN: Statis3.load: file not found: '%s'" % self.strSaveFilename)
            return 0
        try:
            self.dAllTitle = json.load(f)
        except BaseException as err:
            print("INF: Statis3.load: potential error (or file empty): %s" % str(err) )
        print("GOOD: Statis3.load: %s activitie(s) loaded." % len(self.dAllTitle) )
    
        
    def addTime( self, strTitle, rDuration ):
        try:
            self.dAllTitle[strTitle] += rDuration
        except KeyError:
            self.dAllTitle[strTitle] = rDuration
            
    def printAll( self ):
        print("\nINF: Statis3.printAll:")
        for k,v in sorted(self.dAllTitle.items(), key=lambda x: x[1],reverse=True):
            print( "%5.0fs: %s" % (v,k) )
            
    
# class Statis3 - end
        
        
def run_statis():
    statis3 = Statis3()

    prevTitle = ""
    rTimeLoopSec = 1.

    timeLastSave = time.time()

    while 1:
        strTitle = getCurrentWindowTitleName()
        strTitle = strTitle.encode("ascii", errors="namereplace").decode("ascii")
        strTitle = strTitle.replace( " * ", " - " ) # for unsaved document in scite
        strTitle = replaceNameReplaceByNonAccentuatedChars(strTitle)
        strTitle = cleanTitle( strTitle )
        
        bPrivate = False
        if "Mozilla Firefox (navigation privee)" in strTitle:
            if "Messages pour le Web" in strTitle:
                strTitle = "Messages pour le Web"
            else:
                #~ bPrivate = True
                strTitle = "(activite privee)"
                
        if strTitle != "" and not bPrivate:
            if strTitle != prevTitle:
                print("Title: '%s'" % strTitle )
                prevTitle = strTitle
            else:
                # seems like we stay 1 sec more on this window
                statis3.addTime(strTitle,rTimeLoopSec)

        if int(time.time())%20 == 0 and 0:
            statis3.printAll()
            
        if time.time() - timeLastSave > 60:
            timeLastSave = time.time()
            statis3.save()
            
        time.sleep(rTimeLoopSec)
        
if __name__ == "__main__":
    run_statis()

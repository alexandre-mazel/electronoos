import pickle
import os


def normaliseFilename(f):
    """
    change filename to a unique one, 
    eg: 
        facerecognition_dlib.py => C:/Users/alexa/dev/git/face_tools/facerecognition_dlib.py
        ../face_tools/facerecognition_dlib.py => C:/Users/alexa/dev/git/face_tools/facerecognition_dlib.py
        avec / change in os.sep
    """
    if f == None:
        return f
    f = f.replace("/",os.sep)
    f = f.replace("\\",os.sep)
    f=os.path.abspath(f)
    f = f.replace(os.sep+os.sep,os.sep)
    return f
    

class StoredInfo:
    """
    store precomputed information about a file on a disk and allow some statistiques and digging.
    eg:
    you can make a StoredInfo( "facerec_embedding" ) and store all precomputed embedding on a file, then you can access it faster.
    """
    def __init__( self, infoname ):
        self.feats = {} # a dict for each filename => data stored
        self.strSaveFileName = os.path.expanduser("~/cache/stored_info_" + infoname + ".dat" )
        self.bLoaded = False
        self.bMustSave = False
        #~ self.load()
        
    def __del__( self ):
        try:
            self.save()
        except ImportError as err:
            pass
            
    def isLoaded(self):
        return self.bLoaded
        
    def getSaveFileName( self ):
        return self.strSaveFileName
        
    def load( self ):
        if self.bLoaded: return
        
        # format: for each line a name, then pairs of filename and features
        import ast
        timeBegin = time.time()
        self.bLoaded = True
        self.bMustSave = False
        try:
            file = open(self.strSaveFileName, "rt" )
        except: return
        
        print( "INF: StoredFeatures.load: starting..." )
        if 1:
            # use pickle: faster! (0.34s instead of 7.4 on my surface7)
            file.close()
            file = open(self.strSaveFileName, "rb" )
            self.feats = pickle.load(file)
            file.close()
            print( "INF: StoredFeatures.load: end (loaded user: %d) (duration:%5.2fs)" % (len(self.feats), time.time() - timeBegin) )
            print( "INF: StoredInfo.load: user "": nbr feats: %d" % (len(self.feats[""]) ) )
            return


    def save( self, bForceWrite = False ):
        # WRN: the order in the file is different than the format in memory (feature at the end instead in [1])
        
        if not self.bMustSave and not bForceWrite:
            return
        print( "INF: StoredInfo.save: starting..." )
        
        if not self.isLoaded:
            print( "INF: StoredInfo.save: StoredInfo not loaded => not saving" )
            return
        
        
        self.bMustSave = False
        
        if 1:
            # use pickle: faster!
            outfile = open(self.strSaveFileName,'wb')
            pickle.dump(self.feats,outfile, protocol=pickle.HIGHEST_PROTOCOL)
            outfile.close()
            print( "INF: StoredInfo.save: end" )
            return
        
    def getDatas( self, strFilename ):
        """
        return info associated to this user or [] if this file has been precomputed with no result
        or None if not found
        """
        bVerbose = 1
        bVerbose = 0
        if bVerbose: print("DBG: getDatas: looking for '%s'" % strFilename )
        strFilename = normaliseFilename(strFilename)
        if bVerbose: print("DBG: getDatas: normalised: '%s'" % strFilename )
        
        if strFilename in self.feats:
            return self.feats[strFilename]
        return None
        
    def storeDatas( self, strFilename, datas, bForceStoring = False ):
        """
        features can be [] if no face found in the image
        """
        if strFilename == None or strFilename == "":
            print("WRN: StoredInfo.storeDatas: called with strFilename: %s" % strFilename )
            return False
            
        strFilename = normaliseFilename(strFilename)
        
        if self.getDatas(strFilename) != None and not bForceStoring:
            print( "WRN: StoredInfo.storeDatas: %s already added" % (strFilename) )
            return False
        
        strDebug = str(datas)
        if len(strDebug) > 60: strDebug = strDebug[:60] + "..."
        
        print( "INF: StoredInfo.storeDatas: adding info for '%s': %s" % (strFilename,strDebug) )
        self.feats[strFilename] = datas
        self.bMustSave = True
        return True
        
    def informFileRenamed( self, strOldFilename, strNewFilename ):
        """
        takes note a file have been renammed (used only time optimisation reason, when renamming during labelling)
        return True if everything's ok
        """
        print( "INF: StoredInfo.informFileRenamed: %s => %s" % (strOldFilename,strNewFilename) )
        try:
                self.feats[strNewFilename] = self.feats.pop(strOldFilename)
                return True
        except KeyError:
            print( "WRN: informFileRenamed: '%s' is not in the dict" % strOldFilename )
            pass

        # this filename is unknown
        return False

                
# class StoredInfo - end

def autotest():
    sto = StoredInfo( "autotest" )
    try:
        os.unlink( sto.getSaveFileName() ) # clean test
    except FileNotFoundError: pass
        
    print( sto.getDatas( "tutu" ) )
    ret = sto.storeDatas( "tutu", 123 )
    assert( ret )
    
    ret = sto.storeDatas( "tutu", 123 )
    assert( not ret )
    
    sto.storeDatas( "tata", "456" )
    sto.storeDatas( "toto", [] )
    
    print( sto.getDatas( "tutu" ) )
    assert( sto.getDatas( "tutu" ) == 123 )
    
    print( sto.getDatas( "tata" ) )
    assert( sto.getDatas( "tata" ) == "456" )
    
    print( sto.getDatas( "toto" ) )
    assert( sto.getDatas( "toto" ) == [] )
    
    sto.save()
    
    

if __name__ == "__main__":
    autotest()
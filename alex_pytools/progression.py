import io
import json
import os
import sys
import time


"""
memorize the progression of different users using file to store it permanently
"""

import misctools
from misctools import assert_equal
from misctools import ExclusiveLock

class Progression:
    """
    enable the storage of a progress in a task, a book, 
    a dialog of a user and the last time the progress append.
    store on disk for permanent storage.
    A same user can have different category of progression (many books at the same time...)
    
    """
    def __init__( self, strSaveFilename = "" ):
        self.strSaveFilename = strSaveFilename # not saved in file
        if self.strSaveFilename == "": 
            self.strSaveFilename = misctools.getPathSave() + "progress.dat"
            
        self.timeLastLoaded = 0.0 # not saved in file
            
        self.dictProg = {} # store a pair user__id => (timestamp,step)
        
    def log( self, str ):
        f = open( "/tmp/progression.log", "at")
        print("LOG: " + str)
        f.write(str+"\n")
        f.close()
        
    @staticmethod
    def _createKey(strUserId,strObjectId):
        return "%s__%s" % (strUserId,strObjectId)
        
    def _assumeExist( self, strUserId,strObjectId, nInitStep = 0 ):
        k = Progression._createKey(strUserId,strObjectId)
        if k in self.dictProg: return
        self.dictProg[k] = [misctools.getTimeStamp(),nInitStep]
        
    def update( self, strUserId, strObjectId, nNewStep ):
        self._assumeExist(strUserId, strObjectId)
        k = Progression._createKey(strUserId,strObjectId)
        self.dictProg[k] = [misctools.getTimeStamp(),nNewStep]
        
        
    def inc( self, strUserId, strObjectId, nIncStep = 1 ):
        self._assumeExist(strUserId, strObjectId)
        k = Progression._createKey(strUserId,strObjectId)
        self.update(strUserId, strObjectId, self.dictProg[k][1]+nIncStep)
        
    def get(self,strUserId, strObjectId, defaultValue = None):
        k = Progression._createKey(strUserId,strObjectId)
        try:
            return self.dictProg[k][1]
        except KeyError:
            pass
        return defaultValue
        
    def getAndInc(self,strUserId, strObjectId, defaultValue = None, nIncStep = 1 ):
        """
        get and inc in one call
        armoured !
        """
        
        lock = ExclusiveLock()
        lock.acquire()
        
        self.load()
        v = self.get(strUserId, strObjectId, defaultValue)
        self.inc(strUserId, strObjectId, nIncStep)
        self.save()
        lock.release()
        
    def delProgress(self,strUserId, strObjectId):
        k = Progression._createKey(strUserId,strObjectId)
        try:
            del self.dictProg[k]
            return True
        except KeyError:
            pass
        return False
        
    def load( self ):
        # will load every time it's usefull, but not more.
        
        try:
            if self.timeLastLoaded > os.path.getmtime(self.strSaveFilename):
                #warning: changing strSaveFilename after load can prevent real loading!
                return 0
        except (common.FileNotFoundError, OSError) as err: 
            print("DBG: Progression.load: FileNotFoundError: " + str(err) )
            pass
        
        self.timeLastLoaded = time.time()
        print("DBG: Progression.load: loading from '%s'" % self.strSaveFilename)
        try:
            f = io.open(self.strSaveFilename,"rt", encoding='cp1252')
        except common.FileNotFoundError:
            s = "WRN: Progression.load: file not found: '%s'" % self.strSaveFilename;
            self.log(s)
            return 0
        dictlist = json.load(f)
        if sys.version_info[0] >= 3:
            self.dictProg = dictlist
        else:
            self.dictProg = {};
            for k,d in dictlist.items():
                d[0] = str(d[0])
                self.dictProg[str(k)] = d
        self.log("INF: Progression.load: loaded: %d progression(s)" % (len(self.dictProg)) )
        f.close()
        
        return 1
        
    def save( self ):
        self.log("DBG: Progression.save: saving %s prog(s) to '%s'" % (len(self.dictProg),str(self.strSaveFilename)) )
        f = io.open(self.strSaveFilename,"wt", encoding='cp1252')
            
        if sys.version_info[0] >= 3:
            ret = json.dump((self.dictProg),f,indent=2, ensure_ascii=False)
        else:
            data = json.dumps((self.dictProg),indent=2, ensure_ascii=False)
            data = data.encode("cp1252")
            data = unicode(data)
            f.write(data)
        
        f.close()
        self.timeLastLoaded = time.time() # prevent reloading next time
        
    def __str__(self):
        o = ""
        o += str(self.dictProg)
        return o
        
# class Progression - end
        
progress = Progression()
        
def autotest():
    strTestFilename = "/tmp/progression_test.dat"        
    
    try: os.unlink(strTestFilename)
    except (misctools.FileNotFoundError,OSError) as err: print("WRN: normal error?: " + str(err))
    
    pm = Progression(strTestFilename)

    name = "Jean pierre"
    name2 = "Alain"
    id = "id_1"
    pm.update(name,"id_0",100)
    pm.update(name,id,3)
    assert_equal(pm.get(name,id),3)
    
    pm.update(name,id,4)
    assert_equal(pm.get(name,id),4)
    
    pm.inc(name,id)
    progress = pm.get(name,id)
    assert_equal(progress,5)
    
    assert_equal(pm.get("unknown",id),None)
    assert_equal(pm.get(name,"id_unk"),None)


    pm.save()
    
    print("- saved:")
    print(pm)
    
    pm2 = Progression(strTestFilename)
    pm2.load()
    print("- reloaded:")
    print(pm2)
    
    assert_equal(str(pm),str(pm2))
    
    assert_equal(pm2.get(name,id),5)
    
    pm.delProgress(name,id)
    assert_equal(pm.get(name,id),None)
    assert_equal(pm2.get(name,id),5)
        
    #~ pm.delUser(name)  # complicated
    
    assert(str(pm)!=str(pm2))
    
        
if __name__ == "__main__":
    autotest()

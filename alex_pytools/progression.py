
"""
store the progression of different users using file to store it
"""


class Progression:
    """
    enable the storage of a progress in a task, a book, 
    a dialog of a user and the last time the progress append.
    store on disk for permanent storage.
    A same user can have different category of progression (many books at the same time...)
    
    """
    def __init__( self ):
        self.dictProg = {} # store a pair user__id => (timestamp,step)
        
    @staticmethod
    def _createKey(strUserId,strObjectId):
        return "%s__%s" % (strUserId,strObjectId)
        
    def _assumeExist( self, strUserId,strObjectId, nInitStep = 0 ):
        k = _createKey(strUserId,strObjectId)
        if k in self.dictProg: return
        self.dictProg[k] = nInitStep
        
    def update( self, strUserId, strObjectId, nNewStep ):
        self._assumeExist(strUserId, strObjectId)
        k = _createKey(strUserId,strObjectId)
        self.dictProg[k] = nNewStep
        
        
    def inc( self, strUserId, strObjectId, nIncStep = 1 ):
        self._assumeExist(strUserId, strObjectId)
        k = _createKey(strUserId,strObjectId)
        self.update(strUserId, strObjectId, self.dictProg[k]+nIncStep)
        
    def load( self ):
        # will load every time it's usefull, but not more.
        
        try:
            if self.timeLastLoaded > os.path.getmtime(self.strSaveFilename):
                #warning: changing strSaveFilename after load can prevent real loading!
                return 0
        except (common.FileNotFoundError, OSError) as err: 
            print("DBG: DediManager.load: FileNotFoundError: " + str(err) )
            pass
        
        self.timeLastLoaded = time.time()
        print("DBG: DediManager.load: loading from '%s'" % self.strSaveFilename)
        try:
            f = io.open(self.strSaveFilename,"rt", encoding='cp1252')
        except common.FileNotFoundError:
            s = "WRN: DediManager.load: file not found: '%s'" % self.strSaveFilename;
            self.log(s)
            return 0
        dictlist = json.load(f)
        self.dedis = {};
        for k,d in dictlist.items():
            self.dedis[k] = Dedi.constructFromList(d)
        self.log("INF: DediManager.load: loaded: %d dedi(s)" % (len(self.dedis)) )
        f.close()
        
        return 1
        
    def save( self ):
        self.log("DBG: DediManager.save: saving %s dedi(s) to '%s'" % (len(self.dedis),str(self.strSaveFilename)) )
        f = io.open(self.strSaveFilename,"wt", encoding='cp1252')
        dictlist = {}
        for k,r in self.dedis.items():
            dictlist[k] = r.toList()
            
        if sys.version_info[0] >= 3:
            ret = json.dump((dictlist),f,indent=2, ensure_ascii=False)
        else:
            data = json.dumps((dictlist),indent=2, ensure_ascii=False)
            data = data.encode("cp1252")
            data = unicode(data)
            f.write(data)
        
        f.close()
        self.timeLastLoaded = time.time() # prevent reloading next time
        
        
def autotest():
    if 1:
        if os.name == "nt" or 1:
             # ne pas activer ce code après le developement!
            lock = common.getLockForTools()
            lock.release(bForceReleaseAny = True, bVerbose=True)
            
    dm = DediManager()
    strTestFilename = "/tmp/dedi_manager_test.dat"
    try: os.unlink(strTestFilename)
    except (common.FileNotFoundError,OSError) as err: print("WRN: normal error?: " + str(err))
    dm.strSaveFilename = strTestFilename

    idnew = dm.createNewDedi("test1", "toto@test.com")
    ret = dm.addExchange(idnew,["Salut, ca va?", 1, "Continuer"])
    ret = dm.addExchange(idnew,["Au revoir!"])
    ret = dm.updateExchange(idnew,1, ["A bientot!"])
    ret = dm.updateExchange(idnew,4, ["PS: I love you!"])
    
    #~ ret = dm.addExchange(idnew,[u"Tu es un bon élève!"]) # ne fonctionne pas! # on balancera du &eacute;
    assert(ret==True)
    ret = dm.addExchange(123,["Au revoir!"]) # rotten id
    assert(ret==False)
    
    d = dm.getDedi(idnew)
    print("dedi 1:\n" + str(d))
    print("dedi 1 json:\n" + d.toStr(True))

    d = dm.getDedi(123) # rotten id
    print("dedi rotten:\n" + str(d))
    assert(d==None)
    
    s = dm.getAllDedis()
    print("all dedis: " + str(s)) 
    

    dm.save()
    
    print("- saved:")
    print(dm)
    
    dm2 = DediManager()
    dm2.strSaveFilename = strTestFilename
    dm2.load()
    print("- reloaded:")
    print(dm2)
    
    assert(str(dm)==str(dm2))
    
    dm.delDedi(idnew)
    
    assert(str(dm)!=str(dm2))
    
        
if __name__ == "__main__":
    autotest()

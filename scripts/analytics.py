strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools

def updateCounter( sd, astrKeyPath, nInc = 1 ):
    """
    increment a counter in sd, a super dict: a dict of dict of dict... 
    - astrKeyPath is the list of key, eg ["monday", "alexandre", "hand washing"].
    NB: if the key doesn't exists, it will be created at 0.
    """
    d = sd
    for i in range( len(astrKeyPath) ):
        k = astrKeyPath[i]
        if k not in d.keys():
            if i == len(astrKeyPath)-1:
                d[k] = nInc
                return
            d[k] = dict()
        else:
            if i == len(astrKeyPath)-1:
                d[k] += nInc
                return
        d = d[k]
    assert(0)
    
class Analytics:
    
    def __init__( self, strPostName = "" ):
        """
        - strPostName: used mainly for auto testing
        """
        self.strSaveFileName = os.path.expanduser("~/") + ("analytics%s.dat" % strPostName )
        self.dStatPerDay = dict() # for each day for each app name, for each event for each user id, for each ip then a counter 
        self.load()
        
    def __del__( self ):
        self.save()
        
        
    def save(self):
        f=open(self.strSaveFileName, "wt")
        f.write(repr((self.dStatPerDay,self.nCptRestartToday)))
        f.close()
        
    def load(self):
        try:
            f=open(self.strSaveFileName, "rt")
            data = f.read()
            reconstructed = eval(data) # harsh unsafe!
            print("DBG: Stater.load: loading: '%s'" % str(reconstructed) )
            self.dStatPerDay, self.nCptRestartToday  = reconstructed
            self.nCptRestartToday += 1
            f.close()  
        except BaseException as err:
            print("WRN: Stater.load: %s" % str(err) )
            return)
            
    def update( self, strIP, strUserID, strAppName, strEvent ):
        strD = misctools.getDayStamp()
        updateCounter(self.dStatPerDay, (strD, strAppName, strEvent, strUserID, strIP) )
        
        
# class Analytics - end

def autoTest():
    a = Analytics("_test")
    
    strIP1 = "192.168.0.1"
    strIP2 = "192.168.0.2"
    u1 = "Alex",
    a1 = "boot"
    a2 = "telepresence"
    e1 = "start"
    e2 = "stop"
    a.update( strIP1, u1, a1, e1 )
    a.update( strIP1, u1, a1, e2 )
    a.update( strIP1, u1, a1, e1 )
    a.update( strIP1, u1, a1, e2 )
    a.update( strIP1, u1, a2, e2 )
    a.update( strIP1, u1, a2, e2 )
    a.update( strIP2, u1, a2, e2 )
    
# autoTest - end

        
        
        
        
        
        

class Rooms:
    def __init__( self ):
        self.dictDesc = dict()
        
        
    def loadFromDisk( self, strFilename = "rooms.txt"):
        f = open(strFilename)
        while 1:
            line = f.readline()
            if line == "":
                break
            print("DBG: Rooms.loadFromDisk: line: '%s'" % line )
            strName = "203" # TODO
            strDesc = "desc de la salle TODO" # TODO
            self.dictDesc[strName]=strDesc
            
        f.close()
        
        
    def getDesc( self, strName ):
        try:
            return self.dictDesc[strName]
        except BaseException as err:
            print( "WRN: Rooms.getDesc: err: %s" % err)
        return 
        
# class Rooms - end

rooms = Rooms()
rooms.loadFromDisk()

def auto_test():
    name = "203"
    print("salle %s => %s" % (name, rooms.getDesc(name) ) )

if __name__ == "__main__":
    auto_test()
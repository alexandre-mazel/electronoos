
def getUserName():
    return "pipotest"
    
def getUserName( clientAddress, strUserAgent ):
    astrName = [ "Rocky", "Marianne", "Jean-Pierre", "Telemaque", "Nono", "Adrienne", "Francis", "Polo", "Juniper", "Phileas", "Clem" ]
    nUserHash = hash(strUserAgent) + hash(clientAddress[0])
    return astrName[nUserHash%len(astrName)]+str(nUserHash%100)
            
class User:
    def __init__( self, strUserName ):
        self.strUserName = strUserName
        self.reset()
        
    def reset( self ):
        self.listSong = ["song1", "song2", "song3", "song4", "song5", "song6", "song7", "song8"]
        self.listSong += self.listSong
        
        
    def gotoNext(self):
        print( "INF: User: %s, gotoNext" % (self.strUserName) )        
        self.listSong.pop(0)
        
    def neg(self):
        strSong = self.listSong[0]
        i = 0
        while i < len(self.listSong):
            if( strSong == self.listSong[i] ):
                del self.listSong[i]
            else:
                i+=1
        
    def getPlaylist( self ):
        return self.listSong

        
class Users:
    def __init__(self):
        self.allUsers = {}
        
    def getUser( self, strUserName ):
        try:
            return self.allUsers[strUserName]
        except:
            self.allUsers[strUserName] = User(strUserName)
        return self.allUsers[strUserName]
        
    
users = Users()

def getAllCommands():
    return [
                "next",
                "neg",
                "reset"
                ]

def generateCommandsLinks():
    strOut = "<br>\n"
    for command in getAllCommands():
        strOut += '<A HREF = "?%s">%s</A><BR>\n' % (command, command)
    return strOut

def run( clientAddress, strUserAgent, astrCommand = [] ):
    print( "INF: skipit.run: astrCommand: %s" % astrCommand )
    strOut = ""
    strUserName = getUserName(clientAddress, strUserAgent)
    strOut  += "User: %s<br>\n" % strUserName
    user = users.getUser(strUserName)
    for strCommand in astrCommand:
        strOut  += "Command: %s<br>\n" % strCommand
        if( strCommand == "next" ):
            user.gotoNext()
        if( strCommand == "neg" ):
            user.neg()
        if( strCommand == "reset" ):
            user.reset()
            
    strOut  += "Next List: %s<br>\n" % str(user.getPlaylist())
    
    strOut += generateCommandsLinks()
    return strOut
    

    
if __name__ == "__main__":
    clientAddress = ('192.168.0.100', 52407)
    strUserAgent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:32.0) Gecko/20100101 Firefox/32.0"
    print run(clientAddress, strUserAgent)
    print run(clientAddress, strUserAgent, ["next"])
    print run(clientAddress, strUserAgent, ["neg"])
    print run(clientAddress, strUserAgent, ["reset"])

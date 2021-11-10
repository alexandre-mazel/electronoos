from versatile import Versatile
import cv2
import datetime
import os
import sys
import time
sys.path.append("../../face_tools/" )
try: import facerecognition_dlib
except BaseException as err: print( "WRN: no facerecognition algorithm found? or error while loading ERR: %s" % str(err))

"""
encrypt/decrypt
import Crypto
from Crypto.PublicKey import RSA
from Crypto import Random

random_generator = Random.new().read
key = RSA.generate(1024, random_generator) #generate public and private keys

publickey = key.publickey # pub key export for exchange

encrypted = publickey.encrypt('encrypt this message', 32)
#message to encrypt is in the above line 'encrypt this message'

print 'encrypted message:', encrypted #ciphertext

f = open ('encryption.txt', 'w'w)
f.write(str(encrypted)) #write ciphertext to file
f.close()

#decrypted code below

f = open ('encryption.txt', 'r')
message = f.read()

decrypted = key.decrypt(message)

print 'decrypted', decrypted

f = open ('encryption.txt', 'w')
f.write(str(message))
f.write(str(decrypted))
f.close()

// save key to a file
from Crypto.PublicKey import RSA
private_key = RSA.generate(1024)
public_key = private_key.publickey()
print(private_key.exportKey(format='PEM'))
print(public_key.exportKey(format='PEM'))

with open ("private.pem", "w") as prv_file:
    print("{}".format(private_key.exportKey()), file=prv_file)

with open ("public.pem", "w") as pub_file:
    print("{}".format(public_key.exportKey()), file=pub_file)
"""
    

def getFilenameFromTime(timestamp=None):
    """
    get a string usable as a filename relative to the current datetime stamp.
    eg: "2012_12_18-11h44m49s049ms"

    timestamp : time.time() returned value
    """
    if timestamp is None:
        datetimeObject = datetime.datetime.now()
    elif isinstance(timestamp, datetime.datetime):
        datetimeObject = timestamp
    else:
        datetimeObject = datetime.datetime.fromtimestamp(timestamp)
    strTimeStamp = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" );
    strTimeStamp = strTimeStamp.replace( "000ms", "ms" ); # because there's no flags for milliseconds
    return strTimeStamp;
  
def getTimeStamp():
    """
    get a time stamp humanly comprenhensive
    eg: "2012_12_18-11h44m49s049ms"
    v0.7
    """
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss" );
    # retrieve some interesting ms
    t = time.time()
    strTimeStamp += "%03dms" % int( (t - int(t)) * 1000)
    return strTimeStamp
  
class Algorithms:
    def __init__( self, facereco, facedetect = None, objectreco = None ):
        self.facereco = facereco
        self.facedetect = facedetect
        self.objectreco = objectreco

class CloudServicesServer( Versatile ):
    def __init__(self, nPort, strSavePath = None ):
        if strSavePath == None:
            import getpass
            strSavePath = os.sep + "home" + os.sep + getpass.getuser() + os.sep + "cloud_db" + os.sep
            
        self.strSavePath = strSavePath
        print( "INF: saving all client data to '%s'" % self.strSavePath )
            
        print( "INF: versatile: starting server on port %s" % nPort )        
        Versatile.__init__(self, nPort=nPort)
        self.dictAlgo = dict() # for each client.id a bunch of algorithm
        
        # some global algorithms (that doesn't store anything)
        try:
            print( "INF: versatile: Loading FaceDetection..." )
            sys.path.append( os.path.expanduser("~/dev/git/electronoos/custom_from_ext/") )
            import am_facedetect_aizoo
            self.faceDetectionGlobal =  am_facedetect_aizoo.MaskDetector()
            self.faceDetectionGlobal.loadModels( 'models/face_mask_detection.pb' )
    
        except BaseException as err:
            print( "WRN: facedetection can't be loaded, err: %s" % str(err) )
            self.faceDetectionGlobal  = None
        print( "INF: versatile: Loading FaceDetection - finished" )
    #~ def getFreeDBName( self ):
        #~ """
        #~ Generate a new base name and return it to the user, he will then use it for his own use.
        #~ """
        
    def handleNewClientArrival( self, client ):
        try:
            fr = facerecognition_dlib.FaceRecogniser()
        except Exception as err:
            print( "WRN: handleNewClientArrival: while loading algorithm: %s" % str(err))
            fr = None
        self.dictAlgo[id(client)] = Algorithms(fr)
        if self.dictAlgo[id(client)].facereco != None:
            self.dictAlgo[id(client)].facereco.loadModels()        
            #~ self.dictAlgo[id(client)].facereco.load( self.strSavePath + self.dictClientID[id(client)] )

        return Versatile.handleNewClientArrival( self, client )
        
    def handleClientIdentified( self, client ):
        """
        A client has identified, do what you want in inherited classes...
        """
        if self.dictAlgo[id(client)].facereco != None:
            self.dictAlgo[id(client)].facereco.load( self.strSavePath + str(self.dictClientID[id(client)]) )
        return Versatile.handleClientIdentified( self, client )
        
    def handleClientRemoveIdentification( self, client ):
        """
        this client want to stop using this identification, do what you want in inherited classes...
        """
        if self.dictAlgo[id(client)].facereco != None:
            self.dictAlgo[id(client)].facereco.save( self.strSavePath + str(self.dictClientID[id(client)])  )
            self.dictAlgo[id(client)].facereco = None
        return Versatile.handleClientRemoveIdentification( self, client )
        
        
    def handleClientLeft( self, client ):
        if id(client) in self.dictAlgo.keys():
            if self.dictAlgo[id(client)].facereco != None:
                self.dictAlgo[id(client)].facereco.save( self.strSavePath + str(self.dictClientID[id(client)])  )
                self.dictAlgo[id(client)].facereco = None
        return Versatile.handleClientLeft( self, client )

    def getDebugFolderPath( self, client = None ):
        strSaveDbgPath = "./imgs/"
        if client != None:
            strSaveDbgPath += self.dictClientID[id(client)] + os.sep
        try:
            os.makedirs( strSaveDbgPath )
            print( "INF: CloudServicesServer.getDebugFolderPath: successfully created imgs storing place: %s" % (strSaveDbgPath) )
        except: pass
        return strSaveDbgPath
        
    def handleCommand( self, command, command_parameters, client = None ):
        """
        handleCommand specific to cloud command
        """

            
        print( "%s: INF: CloudServicesServer.handleCommand: %s" % (getTimeStamp(), command) )
        if command == Versatile.nCommandType_Value:
            print( type(command_parameters) )
            print( type(command_parameters[0]) )
            print( type(command_parameters[0][0]) )
            if isinstance( command_parameters, Versatile.VersatileImage ) or isinstance( command_parameters[0], Versatile.VersatileImage ) or isinstance( command_parameters[0][0], Versatile.VersatileImage ):
                print( "OK: got an image..." )
                
                image = command_parameters[0][0] # why an array of tuple of the image and size ?!?
                
                cvim = image.convertToCvImage()
                
                # TODO: launch command on face reco
                # TODO: db handling (not finished yet)
                print( "image.strCommand: '%s'" % str(image.aCommand) )
                cmd = image.aCommand
                if len(cmd) > 0:
                    algoname = cmd[0].lower()
                if len(cmd) > 1:
                    dbname = cmd[1]
                else:
                    dbname = None
                if len(cmd) > 2:
                    command = cmd[2].lower()
                else:
                    command = None                    
                if len(cmd) > 3:
                    params = cmd[3].lower()
                else:
                    params = None
                    
                if algoname == "facerecognition":
                    algo = self.dictAlgo[id(client)].facereco
                    
                    if command == "learn":
                        timeBeginLearn = time.time()
                        #retVal = algo.learn( cvim, params, id=-2 ) # force auto update
                        retVal = algo.continuousLearnFromImg( cvim ) # force auto update
                      
                        if retVal[0] > -100:
                            strID = str(retVal[1])
                            strName = ""
                            cv2.imwrite( self.getDebugFolderPath(client) + getFilenameFromTime() +"_" + strName + strID + ".png", cvim)
                            
                            if retVal[0]>0:
                                # force db save after each big learn
                                self.dictAlgo[id(client)].facereco.save( self.strSavePath + str(self.dictClientID[id(client)])  )
                        else:
                            if 0:
                                # continuous image save
                                cv2.imwrite( self.getDebugFolderPath(client) + getFilenameFromTime() +"_nolearn.png", cvim)                            
                            
                        if self.bVerbose: print( "INF: CloudServicesServer.handleCommand: learn: returning: %s (duration: %5.2fs)" % (str(retVal),time.time()-timeBeginLearn ) )
                        return retVal

                        
                    if command == "recognise":
                        retVal = algo.recognise( cvim, bSpeedUp = False )
                        print( "DBG: retVal: %s (db has %d peoples)" % (str(retVal),algo.getNbrKnownUsers()) )
                        if algo.getNbrKnownUsers() < 1:
                            print( "error: users all disappeared !!!" )
                            exit(-15)
                        strName = "none"
                        strDist = ""
                        if len(retVal) > 0:
                            if len(retVal[0]) > 1:
                                strName = retVal[0][1]
                                strDist = "__" + str(int(retVal[0][2] * 100))
                                
                        cv2.imwrite( self.getDebugFolderPath(client) + getFilenameFromTime() +"_" + strName + strDist + ".png", cvim)
                        
                        
                        if self.bVerbose: print( "%s: INF: CloudServicesServer.handleCommand: recognise: returning: %s" % (getTimeStamp(), str(retVal) ) )
                        return retVal
                        
                    if command == "get_status":
                        # NDEV: send an image, just to receive a status: beurk !!!
                        retVal = [["nbr_known_users",algo.getNbrKnownUsers()]]
                        if self.bVerbose: print( "%s: INF: CloudServicesServer.get_status: recognise: returning: %s" % (getTimeStamp(), str(retVal) ) )
                        return retVal                        
                    
                    print( "INF: CloudServicesServer.handleCommand: image facerecognition command unknown: '%s'" % (command) )
                    return False
                  
                if algoname == "facedetection":
                    retVal = self.faceDetectionGlobal.detectFromImage( cvim, bShowResults = False )
                    # return value are:
                    # a list of detected face: [ [xmin, ymin, xmax, ymax], confidence that it's a face, [properties] ]
                    # with properties, some string, value and confidence, eg: ["mask", 0 or 1, confidence [0..1]
                    if self.bVerbose: print( "%s: INF: CloudServicesServer.handleCommand: facedetect: returning: %s" % (getTimeStamp(), str(retVal) ) )
                    return retVal
                    
                if algoname == "store":
                    strDstName = self.strSavePath + self.dictClientID[id(client)] + os.sep + "stored" + os.sep
                    strDstName += str(time.time())+".png"
                    cv2.imwrite( strDstName, cvim )
                    return True
                if algoname == "broadcast":
                    key = self.dictClientID[id(client)]
                    if not key in self.dictBrodcastedImages:
                        self.dictBrodcastedImages[key] = []
                    if len(self.dictBrodcastedImages[key])>3:
                        self.dictBrodcastedImages[key] = self.dictBrodcastedImages[key][:-3]
                    vim = Versatile.VersatileImage()
                    vim.createFromCvImage( cvim)
                    print( "INF: storing new image for broadcasting of client %s" % key )
                    self.dictBrodcastedImages[key].append( vim )
                    return True
                print( "INF: CloudServicesServer.handleCommand: image algoname unknown: '%s'" % (algoname) )
                return False
                    
                
        # other command keep standard behavior
        return Versatile.handleCommand( self, command, command_parameters, client )
    # handleCommand - end
    
# class CloudServicesServer - end
nPort = 13000
if len(sys.argv)>1: nPort = int(sys.argv[1])
cs = CloudServicesServer(nPort=nPort)
cs.bVerbose = True
cs.runServer()

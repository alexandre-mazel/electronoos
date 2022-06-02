# -*- coding: utf-8 -*-
###########################################################
# Send data from a simple device (raspberry, gpu, watch) to another device
# version 0.5
# syntaxe:
#       python this_script_name remote_ip dataname [value] or python this_script_name start_server
#       eg: python this_script_name 192.168.0.4 HeadTouched
#           will return "1"
#       eg: python this_script_name 192.168.0.4 step 5
#           will return set the data step to "5"
# Aldebaran Robotics (c) 2008 All Rights Reserved
# NB:
# To kill python processus on windows:
# taskkill /im python.exe /f
###########################################################

"""
cd dev\git\protolab_group\scripts\versatile_almemory\
python versatile.py start_server
"""

try: import cv2
except: print( "WRN: OpenCV2 not found, using cv2 methods will fail" )
try: import numpy as np
except: print( "WRN: numpy not found, using numpy methods will fail" )
import socket
import struct
import sys
import time

def myOrd( a ):
    if sys.version_info[0] < 3:
        return ord(a)
    return a
    
def stringToBytes(s):
    """
    convert string to bytes, whatever the python version
    """
    
    # due to recursing into list, if the string is already bytified, do nothing !
    if not isinstance( s, str ):
        return s
        
    if sys.version_info[0] < 3:
        return s
    data = bytes()
    for i in range(len(s)):
        data += struct.pack( 'c', s[i].encode('ascii') ) # 'UTF-8'
    return data
    

def _waitSizedData( socket_object, bVerbose = False ):
    """
    wait for an int little endian formatted, followed by this amount of data
    return (data (without size field), size)
    data can be None, meaning the connection has been closed
    """
    try:        
        data = socket_object.recv(4) # [Errorno 104]: Connection reset by peer !
    except Exception as err:
        print( "ERR: Versatile._waitSizedData: exception(1): %s" % str(err) )
        return None, 0
        
    nCptNoData = 0
    while( len(data) < 4 ):
        #~ print( "DBG: versatile._waitSizeData. data too short and receiving zero ?!? (end cnx?)" )
        time.sleep( 0.4) # warning, all server is blocked at this point !!! (at least on windows)
        data = socket_object.recv(4)
        nCptNoData += 1
        if nCptNoData > 2:
            print( "WRN: versatile._waitSizeData. client '%s' disappear, closing..." % str(socket_object.getpeername() ) )
            return None, 0
    #~ print( "DBG: Versatile._waitSizedData: 4 bytes received: '%s' (len:%d)" % (str(data),len(data)) ) 
    nWaitedSize = struct.unpack( "<I", data )[0]
    #print( "DBG: Versatile._waitSizedData: packet waited size: %s" % str(nWaitedSize) ) 
    nSize = 0
    if 0:
        data = []
        while nSize < nWaitedSize:
            data.append( socket_object.recv(1) )
            nSize += 1
            #~ print( "DBG: Versatile._waitSizedData: packet current size: %d/%d" % (nSize,nWaitedSize) ) 
    else:
        if nWaitedSize > 3*1024*1024: # max 3 Mo
            print( "ERR: packet to big, error reading? (size:%s)" % str(nWaitedSize) )
            print( "data: %s" % str(data) )
            if 1:
                databuf = socket_object.recv(1024*1024) # flushing a fair amount #recvall ?
                print( "DBG: flushed: %s" % len(databuf) )            
            time.sleep(1)
            return None,0
        try:
            data = socket_object.recv(nWaitedSize) # TODO: is there a timeout that we can increase? (to prevent the patch below)
            if len(data) != nWaitedSize:
                if 0: print( "WRN: Versatile._waitSizedData: size is different %s!=%s (will continue to read, until ok)" % (nWaitedSize, len(data)))
                if 1:
                    while len(data)< nWaitedSize:
                        data += socket_object.recv(nWaitedSize-len(data))
                        time.sleep(0.001)
                
        except Exception as err:
            print( "ERR: Versatile._waitSizedData: exception: %s" % str(err) )
            print( "DBG: Versatile._waitSizedData: packet waited size: %s" % str(nWaitedSize) )
            if 0:
                # try to open close
                ip, port = socket_object.getpeername()
                print( "ip: %s" % ip )
                print( "port: %s" % str(port) )
                print( "WRN: versatile._waitSizeData. client '%s' error, reopening..." % str( ) )
                socket_object.shutdown(socket.SHUT_RDWR);
                socket_object.close()
                socket_object.connect((ip,port))
            return None, 0 # Alma 2018-10-23: adding this return, not so sure...
            
    #~ print( "DBG: Versatile._waitSizedData: data: %s (len:%d)" % (str(data),len(data) ) ) 
    #~ print(dir(socket_object))

    return ( data, nSize )

class Versatile:
    """
    Send data from a simple device (raspberry, gpu, watch) to a robot thru ALMemory.
    
    Datas are passed thru socket (default port is 10001) using this packet format:
    (using little endian format)
    
    0: Packet size: size of the packet excluding this field - DWORD
    4: Command or type - CHAR
                            0: ping - check working - will always return a value 1
                            1: value. followed by a value. eg, an answer to some command...
                            2: get value from a named variables container (eg a STM). followed by a string (cf string)
                            3: set value to a named variables container (eg a STM). followed by a string and a value (cf value multi type style) - will return True or False if error
                            
                            4: ask for a new client ID  - (no param) - return a string
                            5: set client ID (for future call) - (param: id value (string))
                            6: set a parameter related to this client - (param: parameter_name, parameter_value)
                            7: get this parameter  - (param: parameter_name)
                            
                            10: register for an image stream. followed by a camera index (0..255), a resolution (see VersatileResolution), an image format (see VersatileImageFormat) and a required fps (1..1000).
                            11: unregister from an image stream. followed by the camera index, resolution and format (NB: you can't ask twice for the same (camera,res,and format)
                            20: register for a sound stream
                            21: unregister from the sound stream
                            
                            30: get a broadcasted image - followed by a broadcaster id
                            
    5: Command parameters
        length dependant of the command
        
    # all packet send will be acknowledged with at least a 1
    
    
    """
    nCommandType_EOC   = -1
    nCommandType_Ping   = 0
    nCommandType_Value = 1
    nCommandType_Get    = 2
    nCommandType_Set    = 3
    
    nCommandType_CreateClientID       = 4
    nCommandType_SetClientID            = 5
    nCommandType_SetClientParam     = 6
    nCommandType_GetClientParam     = 7
    
    nCommandType_SubscribeCamera    = 10
    nCommandType_UnsubscribeCamera    = 11
    nCommandType_SubscribeSound    = 20
    nCommandType_UnsubscribeSound    = 21
    
    nCommandType_GetBroadcasted    = 30
    
    @staticmethod
    def  isCommandRequiringDataName( nNumCommand ):
        return nNumCommand == Versatile.nCommandType_Get \
            or nNumCommand == Versatile.nCommandType_Set \
            or nNumCommand == Versatile.nCommandType_GetClientParam \
            or nNumCommand == Versatile.nCommandType_SetClientParam \
            or nNumCommand == Versatile.nCommandType_GetBroadcasted

    @staticmethod
    def  isCommandRequiringValue( nNumCommand ):            
        return nNumCommand == Versatile.nCommandType_Value \
            or nNumCommand == Versatile.nCommandType_Set \
            or nNumCommand == Versatile.nCommandType_SetClientID \
            or nNumCommand == Versatile.nCommandType_SetClientParam
            
        
    class VersatileString:
        """
        a string stored in a string starting by the length of the string.
        0: length of the stringin byte (DWORD)
        4: string (...)
        """
        def __init__( self, s = "" ):
            self.s = s
            
        def set( self, s ):
            self.s = s
            
        def toPacket( self ):
            """
            convert object to string
            """
            data = struct.pack('<I', len(self.s)) # '<' => little endian
            #~ data += self.s
            # python 3 want explicit conversion (that's not so silly)
            #~ data += struct.pack("s", self.s.encode('ascii'))
            #~ for i in range(len(self.s)):
                #~ data += struct.pack( 'c', self.s[i].encode('ascii') ) # 'UTF-8'
            data += stringToBytes( self.s )
            
            
            #~ print( "DBG: len data: %s" % len(data) )
            
                
            return data
 
        @staticmethod
        def fromPacket( data, nOptionnalSize = -1 ):
            """
            decode a string from a packet
            return value, size used by the value in data
            """
            if nOptionnalSize == -1:
                nSize = struct.unpack_from("<I",data)[0]
                nOffset = 4
            else:
                nSize = nOptionnalSize
                nOffset = 0
                
            if sys.version_info[0] < 3:
                s = data[nOffset:nOffset+nSize]
            else:
                s = ""
                #~ print(" nSize: %s" % nSize )
                for i in range(nSize):
                    c = struct.unpack_from("<c",data[nOffset+i:nOffset+nSize+i])[0]
                    #~ print( "c: %s" % c )
                    c = c.decode('UTF-8')
                    s += str(c)
            
            return s, nSize+4          
    # class VersatileString - end

    @staticmethod
    def autodetectType( v ):
        #~ print( "DBG: type v: %s" % str(type(v)) )
        if v == None:
            return 0
        if isinstance( v, int ) or isinstance( v, bool ):
            return 1 
        if sys.version_info[0] < 3: # in python3 int type has now an unlimited length
            if isinstance( v, long ):
                if v > 0x7FFFFFFF:
                    print( "WRN: Versatile: truncation of long to int, value: %d" % v )
                return 1             
        if isinstance( v, float ): # NB: True for both Unicode and byte strings
            return 2
        if isinstance( v, str ): # NB: True for both Unicode and byte strings # basestring change so str to switch to python3
            return 3
        #if isinstance( v, Versatile.VersatileImage ): #v est de type instance !
        #~ print(dir(v))
        #~ print(hasattr(v,"bIsGrey"))
        #~ print("str: %s" % str(str(v)) )
        if( hasattr(v,"bIsGrey") ): # CRADO !!!
            return 4
            
        if isinstance( v, list ) or isinstance( v, tuple ) :
            return 9
            
        print( "ERR: Versatile.autodetectType: unable to detect type of '%s' (current type: %s)" % ( str(v), str(type(v)) ) )
        return 0
            
    class VersatileValue:
        """
        a value stored in a string compound of a length+type+data. 
        0: length the length taken by the data (without the type) in byte (DWORD)
        4: type (BYTE)
            1: int (or boolean converted to int)
            2: float
            3: string
            4: image
            5: audio chunk
            9: list of versatile values
            ...
        5: data (...)
        """
        nValueType_None   = 0
        nValueType_Int      = 1
        nValueType_Float   = 2
        nValueType_String = 3
        nValueType_Image = 4 # (see VersatileImage)
        nValueType_AudioChunk = 5 # (see VersatileAudioChunk)
        nValueType_List = 9 # list of VersatileValue
          
        def __init__( self, value = None, nNumEnsureType = None ):
            self._set( value, nNumEnsureType )
            
        def _set( self, value, nNumEnsureType ):
            if isinstance( value, Versatile.VersatileValue ):
                # construct from a VersatileValue
                self.v = value.v
                assert( nNumEnsureType == None ) # can't force a type when passing a VersatileValue
                self.nType = value.nType
                return
                
            self.v = value
                
            if nNumEnsureType == None:
                # auto detect
                nNumEnsureType = Versatile.autodetectType(value)
            self.nType = nNumEnsureType
            
            if isinstance( self.v, bool ):
                if self.v: self.v = 1
                else: self.v = 0
                
        def set( self, value, nNumEnsureType = None ):
            self._set( value, nNumEnsureType )
            
        def toPacket( self ):
            """
            convert object value to string
            """
            if 0: print( "DBG: VersatileValue.toPacket: packeting a value of type %s, value: '%s'" % ( str(self.nType), str(self.v) ) ) 
            
            #print struct.calcsize('B') #1
            #~ print(str(self))
            #~ print(str(self.v))
            #~ print(str(self.nType))
            if self.v == None:
                data = struct.pack('<I', 0) + struct.pack('B', self.nType)
            else:
                # TODO: perhaps explictly encode data using struct.pack?
                if self.nType == Versatile.VersatileValue.nValueType_Image:
                    vAsString = self.v.toPacket()
                    
                elif self.nType == Versatile.VersatileValue.nValueType_List:
                    # we encode in the data the len of element then elements packetised
                    vAsString = struct.pack('<I', len(self.v) )
                    for i in range(len(self.v)):
                        valueToEncode = self.v[i]
                        # sometims VersatileValue can be lazy constructed with some base type included in them (like a list of int, instead of a list of versatilevalue of type int), as it's more efficient, it does'nt hurt...
                        if not isinstance( valueToEncode, Versatile.VersatileValue ):
                            valueToEncode = Versatile.VersatileValue(valueToEncode)
                        vAsString += valueToEncode.toPacket()
                else:
                    # TODO: explicit encoding for string ?
                    vAsString = str(self.v)
                    
                data = struct.pack('<I', len(vAsString)) + struct.pack('B', self.nType) + stringToBytes(vAsString)
            return data
            
        @staticmethod # comme staticmethod, but permits using static class variable nValueType_Int # but some stuffs are then changed.
        def fromPacket( data ):
            """
            decode a value from a packet
            return value, size used by the value in data
            """
            #~ for i in range(min(len(data),8)):
                #~ print( "DBG: data[%d] = %x" % ( i, myOrd(data[i])) )
            nSize = struct.unpack_from('<I',data)[0]
            nType = struct.unpack_from('B',data[4:4+1])[0]
            nIdxStart = 5
            nIdxEnd = 5+nSize
            
            # TODO: perhaps explictly decode data using struct.unpack?

            if nType == Versatile.VersatileValue.nValueType_None:
                value = None
            if nType == Versatile.VersatileValue.nValueType_Int:
                value = int(data[nIdxStart:nIdxEnd])
            elif nType == Versatile.VersatileValue.nValueType_Float:
                value = float(data[nIdxStart:nIdxEnd])
            elif nType == Versatile.VersatileValue.nValueType_String:
                #value = str(data[nIdxStart:nIdxEnd]) # why not using fromPacket de string !!! - DONE
                value = Versatile.VersatileString.fromPacket(data[nIdxStart:nIdxEnd],nSize)[0]
                
            elif nType == Versatile.VersatileValue.nValueType_Image:
                value = Versatile.VersatileImage.fromPacket(data[nIdxStart:nIdxEnd]) # nSize from fromPacket isn't used  ?!?
                
            elif nType == Versatile.VersatileValue.nValueType_List:
                nNbrElement = struct.unpack_from('<I',data[nIdxStart:nIdxStart+4])[0]
                nIdxStart += 4
                value = []
                for i in range(nNbrElement):
                    v,size = Versatile.VersatileValue.fromPacket(data[nIdxStart:]) # we don't now size here
                    nIdxStart += size
                    value.append( v )
            else:
                print( "ERR: VersatileValue.fromPacket, unknown value type: %s" % str(nType) )
            #~ print( "DBG: VersatileValue.fromPacket, decoded value of type %s: %s" % (str(nType), str(value) ) )
            return value, nSize+5            
    # class VersatileValue - end

    class VersatileImage:
        """
        store an image and its metadata
        """
        class WantedResolution:
            # client ask for a resolution that will be matched as nearest possible
            QQVGA=0
            QVGA=1
            VGA=2
            x960=3 # as: 1024x960
            x1024=4 # as: 1280x1024
            x1280=5 # as: 1920x1080

        class Format:            
            GREY=1
            JPG=2
            PNG=3
            RAW=4
            
            
        def __init__( self, bVerbose = False ):
            self.data = None # image data ready for sending (one dimension, string encoded, ...)
            self.aCommand = [] # you can add a list of parameters # see addCommand for doc
            self.bVerbose = bVerbose
            
        
        def createFromCvImage( self, img, timeStamp = None, nFormat = Format.JPG ):
            """
            create a VersatileImage from a cv2.buffer
            """
            if img is None:
                return False
                
            # reducing image
            while img.shape[0]>1080:
                print("WRN: versatile.createFromCvImage: reducing image..." )
                img = cv2.resize( img, (img.shape[1]//2,img.shape[0]//2) )
                
            if timeStamp == None:
                timeStamp = time.time()
            self.timeStamp = int(timeStamp), int(timeStamp*1000)%1000 # on 2 int: seconds & ms
            self.bIsGrey = (nFormat == Versatile.VersatileImage.Format.GREY)
            #self.data = img.reshape( self.nW*self.nH*nChannel,1,1).tostring()
            # encoding:
            #~ print( "DBG: createFromCvImage: encoding format is %d" % nFormat )
            encodeParam = None
            if nFormat == Versatile.VersatileImage.Format.PNG:
                strFormat = ".png"
            if nFormat == Versatile.VersatileImage.Format.JPG:
                strFormat = ".jpg"
                encodeParam = [int(cv2.IMWRITE_JPEG_QUALITY),85]
            
            #~ print( "DBG: createFromCvImage: strFormat is %s" % strFormat )
            #~ print( "DBG: createFromCvImage: self.bIsGrey is %s" % self.bIsGrey )
            timeBegin = time.time()
            self.data = cv2.imencode( strFormat, img, encodeParam )[1].tostring()
            if 1:
                # encryption
                pass
            #~ print( "INF: VersatileImage.createFromCvImage: encoding image takes: %5.3fs" % (time.time()-timeBegin) ) # 0.01 on Pepper in VGA
            #print( "self.img in: %s" % str(img.size) )
            #print( "DBG: VersatileImage.createFromCvImage: compression out: %s in: %s" % ( len(self.data), img.size ) )
            
        def convertToCvImage( self ):
            """
            return a cv2.buffer from a VersatileImage
            """
            #return np.fromstring(self.data, np.uint8).reshape( self.nH,self.nW,nChannel)
            if self.bIsGrey:
                flag = 0
            else:
                try:
                    flag = cv2.CV_LOAD_IMAGE_COLOR # cv2 flag
                except:
                    flag = cv2.IMREAD_COLOR # cv3 flag
            #~ print( "DBG: convertToCvImage: flag is %s" % flag )
            #~ print( "DBG: convertToCvImage: len data: %s" % len(self.data) )
            img = cv2.imdecode(np.fromstring(self.data, np.uint8), flag ) 
            #print( "DBG: VersatileImage.convertToCvImage: decoded size: %s" % ( img.size ) )
            return img
            
        def addCommand( self, listParameter ):
            """
            add a list of command and parameters to this image.
            The remote will send information related to this work
            eg:
                - ["facedetection"] => list face and confidence as an answer
                - ["facerecognition", "db_name", "learn", "some_name"] => True/False and confidence on learning (based on comparison on existing face
                - ["facerecognition", "db_name", "recognise"] => recognition result
                - ["store"] => store this image on some disk
                - ["show"] => show this image on screen
                - ["broadcast"] => show this image to any viewer
                
            """
            for param in listParameter:
                if self.bVerbose: print( "INF: VersatileImage.addCommand: adding '%s'" % str(param) )
                self.aCommand.append(param)
            
        def toPacket( self ):
            """
            convert object value to string
            format: B: is grey, size of data_img, data_img
            """
            #~ print( "DBG: VersatileValue.toPacket: packeting a value of type %s, value: '%s'" % ( str(self.nType), str(self.v) ) ) 
            
            data = struct.pack('B', self.bIsGrey)  \
                        + struct.pack('<I', self.timeStamp[0]) \
                        + struct.pack('<I', self.timeStamp[1]) \
                        + struct.pack('<I', len(self.data)) \
                        + stringToBytes(self.data)
            data += Versatile.VersatileValue( self.aCommand ).toPacket()
            return data
            
        @staticmethod
        def fromPacket( data ):
            """
            decode a value from a packet
            return aVersatileImage, size used by the value in data   
            """
            vi = Versatile.VersatileImage()
            offset = 0
            vi.timeStamp = [0,0]
            if sys.version_info[0] == 3:
                vi.bIsGrey = data[offset]; offset += 1
            else:
                vi.bIsGrey = struct.unpack_from('B',data[offset])[0]; offset += 1
            vi.timeStamp[0] = struct.unpack_from('<I',data[offset:offset+4])[0] ; offset += 4
            vi.timeStamp[1] = struct.unpack_from('<I',data[offset:offset+4])[0] ; offset += 4
            nSize = struct.unpack_from('<I',data[offset:offset+4])[0] ; offset += 4
            #vi.data = struct.unpack_from('B'*nSize,data[offset:offset+nSize]) # $$$$ found method to get a variable decoding!
            vi.data=data[offset:offset+nSize] ; offset += nSize
            #print( "datalen: %s" % (len(vi.data)) )
            
            param, sizeParams = Versatile.VersatileValue.fromPacket(data[offset:])
            print( "DBG: Versatile Image: decoded params: ")
            for i in range( len(param) ):
                print( "%s" % param[i])
            vi.aCommand = param
            offset += sizeParams
            print( "DBG: Versatile Image: decoded params - end")
            return vi, offset
    #class VersatileImage - end
    
    @staticmethod
    def VersatileImage_autoTest():
        print( "INF: VersatileImage_autoTest: starting..." )
        vi = Versatile.VersatileImage()
        w=640
        h = 480
        img = np.zeros((h,w,3), np.uint8)
        for j in range(h):
            for i in range(w):
                img[j,i,0] = i*(j+3)
        img = cv2.imread( "../camera_viewer_at_exit.png" )
        
        vi.createFromCvImage( img, nFormat = Versatile.VersatileImage.Format.PNG)
        imgOut = vi.convertToCvImage()
        assert( np.array_equal( img, imgOut) )
        
        vi.createFromCvImage( img, nFormat = Versatile.VersatileImage.Format.JPG)
        imgOut = vi.convertToCvImage()
        assert( not np.array_equal( img, imgOut) ) # different due to compression loss
        
        vi.createFromCvImage( img, nFormat = Versatile.VersatileImage.Format.PNG)
        data=vi.toPacket()
        vi, size = Versatile.VersatileImage.fromPacket(data)
        imgOut = vi.convertToCvImage()
        assert( np.array_equal( img, imgOut) )
        print( "INF: VersatileImage_autoTest: OK\n" )
            


    #########################################################
    # class Versatile method - start
            
    def __init__( self, nPort = 10001, bVerbose = False ):
        """
        """
        self.bVerbose = bVerbose
        self.nPort = nPort
        self.bMustStop = False
        self.threadSendImage=None
        self.aCameraSubs=[] # for each: client_socket,camera idx, reso, format, period, time last send
        self.dictClientID = dict() # a dict adress of client_socket => logical client ID (as returned by nCommandType_CreateClientID and set by nCommandType_SetClientID
        # NB: logical client ID is internally  a number!!!
        self.dictClientParams = dict() # a dict logical client ID => a dict of parameter (a dict of dict)
        self.dictBrodcastedImages = dict() # a dict logical client ID => a list of stored versatileimages
           
    def setVerbose( self, bVal ):
        self.bVerbose = bVal
        
    def registerToCamera( self, client_socket, nNumCamera, nResolution, nFormat, rPeriod = 0.2 ):
        print( "INF: client %s register for a camera (num camera: %d, res: %d, format: %d, period: %5.2fs)" % ( str(client_socket.getpeername()),nNumCamera, nResolution, nFormat, rPeriod) )
        self.aCameraSubs.append( [client_socket, nNumCamera, nResolution, nFormat, rPeriod, time.time()-100] )
        #self.startThreadSendImage() # can't prevent launching many => done at construction!
        
    def getNewImage( self, nNumCamera, nResolution, nFormat ):
        """
        return (time stamp, image)
        please inherits this method in your own program
        """
        img = np.zeros((480,640,3), np.uint8)
        inc = int(time.time()*100)
        x = (inc%160)
        y = (inc/160)%120
        for i in range(10):
            img[y,x+i,0] = 255 # make it move
            img[y,x+i,1] = 255 # make it move
            img[y,x+i,2] = 255 # make it move
        return (time.time(),img)
        
    def threadSendImageToClient( self ):
        import threading
        print( "DBG: threadSendImageToClient: start..." )
        while( 1 ):
            for i in range( len( self.aCameraSubs ) ):
                client_socket, nNumCamera, nResolution, nFormat, rPeriod, timeLastSend = self.aCameraSubs[i]
                if time.time() - timeLastSend >= rPeriod:
                    self.aCameraSubs[i][-1] = time.time()                    
                    ts, img = self.getNewImage( nNumCamera, nResolution, nFormat )
                    vi = Versatile.VersatileImage()
                    vi.createFromCvImage( img, ts )
                    vv = Versatile.VersatileValue( vi )
                    retVal = self._send( Versatile.nCommandType_Value, None, vv, optionnalClient = client_socket )
                    if retVal == False:
                        print( "INF: threadSendImageToClient: removing client %d" % i )
                        try:
                            del self.aCameraSubs[i]
                        except BaseException as err:
                            print( "WRN: error while deleting: %s" % str(err) )
                        break; # all indexs are offseted, let's restart iteration...
                        # HERE, we could finish this thread if no more subs
            time.sleep(0.01)
            #time.sleep(1.) # to debug
            #~ print( "DBG: threading.currentThread().getName(): %s" % threading.currentThread().getName())
            #~ print(".")
            
    def startThreadSendImage( self ):
        # todo: mutex
        print( "DBG: startThreadSendImage: start" )
        import multiprocessing
        import threading
        if self.threadSendImage != None:
            print( "DBG: startThreadSendImage: already started !!!" )
            return
        #~ print(dir(multiprocessing))
        # self.threadSendImageToClient() # pour tester sans multithreading (mais va locker apres le premier client)
        #self.threadSendImage = multiprocessing.Process( target=self.threadSendImageToClient ).start() # on windows, objects are pickled and socket is'nt picklable so, raise errors
        self.threadSendImage = True # to be sure
        self.threadSendImage = threading.Thread( target=self.threadSendImageToClient ).start() # under windows ne semble pas lancer dans un thread, mais bloque tout le thread
        print( "DBG: startThreadSendImage: end" )
        
        
    def handleCommand( self, command, command_parameters, clientSocket = None ):
        """
        please inherits this method in your own program.
        return None on error
        """
        
        if self.bVerbose: print( "DBG: Versatile.handleCommand: received command: %s,%s" % (command, command_parameters) )

        if not hasattr(self, "simulatedMemory"):
            self.simulatedMemory = dict() # to store command
        
        if command == Versatile.nCommandType_Ping:
            return 1
            
        if command == Versatile.nCommandType_Value:
            print( "WRN: Versatile.handleCommand: Abnormal case: Received this value: %s" % command_parameters )
            return None
            
        if command == Versatile.nCommandType_Get:
            #valueFromALMemory = "(a value taken from ALMemory data named: '%s')" % command_parameters[0]
            #valueFromALMemory = "toto"
            strDataName = command_parameters[0]
            try: 
                valueFromALMemory = self.simulatedMemory[strDataName]
            except:
                if self.bVerbose: print( "DBG: data '%s' isn't in the Memory" % (strDataName) )
                valueFromALMemory = None # non existing value
            return valueFromALMemory
            
            
            
        if command == Versatile.nCommandType_Set:
            strDataName = command_parameters[0]
            value = command_parameters[1]
            if self.bVerbose: print( "DBG: data '%s' should be set to %s" % (strDataName, value) )
            self.simulatedMemory[strDataName] = value
            return 1
            
            
            
        if command == Versatile.nCommandType_CreateClientID:
            time.sleep(0.5)
            nNewClientID = int(time.time()*100)%0x80000000 # the goal is to ensure there won't be two client with same ID. (but that id is storable on a int32)           
            print( "INF: Versatile.handleCommand: creating a new client ID: %s" % nNewClientID )
            return str(nNewClientID)

        if command == Versatile.nCommandType_SetClientID:
            value = str(command_parameters[0])
            if id(clientSocket) in self.dictClientID.keys():
                if self.dictClientID[id(clientSocket)] == value:
                    return 1 # don't do anything...            
                self.handleClientRemoveIdentification( clientSocket )
            if self.bVerbose: print( "INF: client %s has idenfied himself as %s" % ( str(id(clientSocket)), value ) )
            self.dictClientID[id(clientSocket)] = value
            self.handleClientIdentified( clientSocket )
            return 1
            
        if command == Versatile.nCommandType_GetClientParam:
            #valueFromALMemory = "(a value taken from ALMemory data named: '%s')" % command_parameters[0]
            #valueFromALMemory = "toto"
            strDataName = command_parameters[0]
            
            try: 
                clientID = self.dictClientID[id(clientSocket)]
                valueFromParams = self.dictClientParams[clientID][strDataName]
            except:
                if self.bVerbose:  print( "DBG: data '%s' isn't in the client params" % (strDataName) )
                valueFromParams = None # non existing value
            return valueFromParams
            
        if command == Versatile.nCommandType_SetClientParam:
            clientID = self.dictClientID[id(clientSocket)]
            strDataName = command_parameters[0]
            value = command_parameters[1]
            if clientID not in self.dictClientParams.keys():
                if self.bVerbose: print( "INF: Versatile.handleCommand: creating a client param id for client %s" % clientID )
                self.dictClientParams[clientID] = dict()
            self.dictClientParams[clientID][strDataName] = value
            return 1            

         

        if command == Versatile.nCommandType_SubscribeCamera:
            if self.bVerbose: print( "DBG: SubscribeCamera: command_parameters: %s" % str(command_parameters) )
            self.registerToCamera( clientSocket, command_parameters[0], command_parameters[1], command_parameters[2], 1./command_parameters[3] )
            return 1
        
        if command == Versatile.nCommandType_GetBroadcasted:
            #valueFromALMemory = "(a value taken from ALMemory data named: '%s')" % command_parameters[0]
            #valueFromALMemory = "toto"
            strBroadcasterID = command_parameters[0]
            nBroadcasterID = int(strBroadcasterID)
            if not nBroadcasterID in self.dictBrodcastedImages.keys():
                print( "ERR: Versatile.handleCommand: broadcaster %d unknown" %  nBroadcasterID )
                return 0 # unknown client
            return self.dictBrodcastedImages[nBroadcasterID][-1]
            
        print( "ERR: Versatile.handleCommand: Abnormal case: unknown command type: %s" % command )
        return None

            
    # handleCommand - end
    
    def handleNewClientArrival( self, client ):
        """
        A new client arrived, do what you want in inherited classes...
        """
        pass
        
        
    def handleClientIdentified( self, client ):
        """
        A client has identified, do what you want in inherited classes...
        """
        pass
        
    def handleClientRemoveIdentification( self, client ):
        """
        this client want to stop using this identification, do what you want in inherited classes...
        """
        pass            
        
    def handleClientLeft( self, client ):
        """
        Sad news: client left, do what you want in inherited classes...
        """
        pass
    
    def manageClientRequests( self, client ):
        self.handleNewClientArrival( client )
        try:
            while 1:
                command, command_parameters = Versatile._waitPacket(client, self.bVerbose)
                if command == Versatile.nCommandType_EOC:
                    client.close()
                    break
                if self.bVerbose: print( "DBG: versatile.manageClientRequests: before handling command..." )
                valueToReturn = self.handleCommand( command, command_parameters, client )
                self._send( Versatile.nCommandType_Value, None, valueToReturn, client )
        except socket.error as err:
            print( "ERR: when working with client, received error: %s" % err )
            client.close()
        self.handleClientLeft(client)
        
    def runServer( self ):
        """
        run an infinite server
        """
        import threading
        self.startThreadSendImage()
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.socket_server.bind( ('', self.nPort ) )
                break
            except OSError as err:
                print( "ERR: connection error: %s" % str(err) )
                print( "ERR: retrying in 2 sec..." )
                time.sleep( 2 )
        
        print( "INF: versatile.runServer: server ready for client connection on port %s..." % self.nPort )
        
        self.bMustStop = False
        while not self.bMustStop:
            try:
                self.socket_server.listen(5)
                client, address = self.socket_server.accept()
                print( "Versatile: client connect from %s" % str(address) )
                #self.manageClientRequests(client) # only one at a time !
                threading.Thread( target=self.manageClientRequests, args=(client,) ).start() # the ',' after 'client' is important else it's not a tuple
                
            except socket.error as err:
                print( "ERR: when working with client, received error: %s" % err )
                client.close()
        
        self.socket_server.close()
        print( "INF: versatile.runServer: stopped." )
                
    def stopServer( self ):
        print( "INF: versatile.stopServer: stopping..." )
        self.bMustStop = True # known bug: we need to get out of the listen to be stopped !!! :(
        self.disconnect()
        try:
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect( ("localhost", self.nPort)) # so we generate a socket to ourself, weird, but works fine.
        except Exception as err:
            print( "DBG: stopServer: socket already closed? err: %s" % str(err) )
        
        
    def _reconnect( self, bFailSilently = False ):
        try:
            print( "INF: Versatile: connecting to %s:%d" % (self.ip, self.nPort) )
            self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_server.connect((self.ip, self.nPort))
        except socket.error:
            if not bFailSilently:
                raise socket.error( "cannot connect to %s:%d" % (self.ip, self.nPort) )
            else:
                print( "WRN: can't (re)connect to %s:%d" % (self.ip, self.nPort) )
        
    def isConnect( self ):
        pass #TODO
        
    def connect( self, strIP, bPatientMode = True):
        """
        bPatientMode: if set, even if server not present at start, the module will wait
        """
        self.ip = strIP
        self._reconnect(bFailSilently=bPatientMode)
        
    def disconnect( self ):
        self.socket_server.shutdown(socket.SHUT_RDWR);
        self.socket_server.close()
        
    @staticmethod # why !?!
    def _waitPacket( socket_object, bVerbose = False ):
        """
        return a decoded packet as a tuple: (nCommand, command_parameters...)
        can return a nCommand == EOC: connection closed
        """
        p,size = _waitSizedData(socket_object,bVerbose)
        if p == None:
            return (Versatile.nCommandType_EOC,None)
        nCommand = struct.unpack_from("B",p)[0]
        offset = 1
        
        if bVerbose: print( "DBG: Versatile._waitPacket: receive command: %d" % (nCommand) )

        commandParameters = []        
        if Versatile.isCommandRequiringDataName( nCommand ):
            strDataName, size = Versatile.VersatileString.fromPacket(p[offset:])
            commandParameters.append( strDataName )
            offset+=size
            
        if Versatile.isCommandRequiringValue( nCommand ):            
            value, size = Versatile.VersatileValue.fromPacket(p[offset:])
            commandParameters.append( value )
            offset+=size
        
        if nCommand == Versatile.nCommandType_SubscribeCamera:
            for i in range(4):
                value, size = Versatile.VersatileValue.fromPacket(p[offset:])
                commandParameters.append( value )
                offset+=size
            
        return (nCommand, commandParameters)
        
    @staticmethod
    def _waitValue( socket_object ):
        """
        return a decoded value as a python object (but encoded in a packet for more security)
        """        
        #data,size = _waitSizedData(socket_object)
        #value, size = Versatile.VersatileValue.fromPacket(data)
        nCommand, commandParameters = _waitPacket( socket_object )
        assert( nCommand == Versatile.nCommandType_Value )
        return value   
        
    def _send( self, nNumCommand, strDataName = None, value = None, optionnalClient = None ):
        """
        send packet to peer
        strDataName: in case of a stm mode
        value: a list of value to send
        optionnalClient: filed if the process is a server, permits to know the client (at least to print a debug msg)
        return:
            - False on error, or (nCommand, command_parameters...) in case of returned value from complex command
        """

        if self.bVerbose: print( "DBG: Versatile._send: sending command %s, dataname: %s, value: %s" %(nNumCommand,strDataName, value) )

        data = struct.pack('B', nNumCommand)
 
        if nNumCommand == Versatile.nCommandType_SubscribeCamera:
            # value is a tuple
            for v in value:
                print( "DBG: _send: encoding command parameter: %s" % v )
                if self.bVerbose: print( "DBG: _send: encoding command parameter: %s" % v )
                vv = Versatile.VersatileValue(v) 
                data += vv.toPacket()
        else:
            # ca mériterais un petit refactor ca (ce cas particulier est vraiment pas beau)
            if strDataName != None:
                vs = Versatile.VersatileString(strDataName)
                

            vv = Versatile.VersatileValue( value ) # in any case we can create a value, even if it's None
                
            if Versatile.isCommandRequiringDataName( nNumCommand ):
                # we encode the dataname
                data += vs.toPacket()

            if Versatile.isCommandRequiringValue( nNumCommand ):
                # we encode a value
                data += vv.toPacket()

        if self.bVerbose and 0:
            nPrintLen = 64
            print( "DBG: Versatile._send: data to send (without encoded len) (first %d bytes):"  % nPrintLen )
            for i in range(min(nPrintLen, len(data))):
                if isinstance(data[i], int):
                    print( "0x%X " % data[i] ),
                else:
                    print( "s0x%X " % ord(data[i]) ),
            print("" ) # \n

        data = struct.pack('<I', len(data)) + data
        
        if self.bVerbose: print( "DBG: Versatile._send: sending a packet of total size: %s" % str(len(data)) )
        
        socket_object = optionnalClient
        self.bCustomClientSocket = True
        if socket_object == None:
            self.bCustomClientSocket = False
            socket_object = self.socket_server
        
        try:
            socket_object.sendall( data )
        except socket.error as err:
            
            if self.bCustomClientSocket:
                print( "WRN: Versatile.send: got socket error, client disappear? err: %s" % str(err) )
                return False
                
            print( "WRN: Versatile.send: got socket error, serveur out, try to reconnect, err: %s" % str(err) )
            # ne fonctionne pas sous windows?
            self._reconnect(bFailSilently = True)
            socket_object = self.socket_server
            try:
                socket_object.sendall( data )
            except socket.error as err:
                print( "DBG: Versatile.send: socket disconnected, skipping this message, will try to reconnect next time..., err: %s" % str(err) )
                return False
            
        if self.bVerbose: print( "DBG: command sent..." )
        if nNumCommand == Versatile.nCommandType_Value:
            # a returned value never wait for ack
            return [1,[True]]
        
        if self.bVerbose: print( "DBG: waiting for an answer..." )
        retVal = Versatile._waitPacket(socket_object)
        if self.bVerbose: print( "DBG: waiting for an answer: received..." )
        return retVal
        
    def waitPacket( self ):
        """
        wait for some answer
        """
        retVal = Versatile._waitPacket(self.socket_server)
        if self.bVerbose: print( "DBG: waitPacket: returning: %s" % str(retVal ) )
        return retVal
        
        
    def isRunning( self ):
        try:
            retVal = self._send( Versatile.nCommandType_Ping )
            if self.bVerbose: print( "DBG: Versatile: isRunning: received: %s" % str(retVal) )
            return retVal != False and retVal[1][0] == 1
        except Exception as err:
            if self.bVerbose: print( "DBG: Versatile: isRunning: received this err: %s" % str(err) )
        return False
        
        
        
        
    ############### accessor to each command type - use them in your program
        
    def get( self, strDataName ):
        """
        return a pair: sucess,value
        """
        retVal = self._send( Versatile.nCommandType_Get, strDataName )
        if retVal == False:
            return [False,None]
        return [True, retVal[1][0] ]
        
    def set( self, strDataName, value ):
        retVal = self._send( Versatile.nCommandType_Set, strDataName, value )
        #~ print( "DBG: Versatile.set: retVal: %s" % str(retVal) )
        return retVal != False and retVal[1][0] == 1
        
    def sendValue( self, value ):
        retVal = self._send( Versatile.nCommandType_Value, None, value )
        return retVal != False and retVal[1][0] == 1
        
    def sendValueGeneratingResults( self, value ):
        """
        when sending a value generating a result, like an image and its analyse...
        """
        retVal = self._send( Versatile.nCommandType_Value, None, value )
        if self.bVerbose: print( "DBG: sendValueGeneratingResults: retVal: %s" % str(retVal) )
        if retVal == False or retVal[1][0] == 0:
            return False # error in sending values
        return self.waitPacket()
    
    def createClientID(self):
        retVal = self._send( Versatile.nCommandType_CreateClientID )
        if retVal == False:
            return [False,None]
        return [True, retVal[1][0] ]
        
    def setClientID(self, clientID):
        retVal = self._send( Versatile.nCommandType_SetClientID, None, str(clientID) )
        return retVal != False and retVal[1][0] == 1     
        
    def setClientParam(self, strParamName, value ):
        retVal = self._send( Versatile.nCommandType_SetClientParam, str(strParamName), value )
        return retVal != False and retVal[1][0] == 1             

    def getClientParam(self, strParamName, value ):
        retVal = self._send( Versatile.nCommandType_GetClientParam, str(strParamName) )
        if retVal == False:
            return [False,None]
        return [True, retVal[1][0] ] 
        
    def subscribeCamera(self, nCameraIndex, nWantedResolution, nImageFormat, nFps ):
        retVal = self._send( Versatile.nCommandType_SubscribeCamera, None, (nCameraIndex,nWantedResolution,nImageFormat, nFps ) )
        return retVal != False and retVal[1][0] == 1 
        
    def getImage( self ):
        """
        get an Image from a previously subscribed server
        return False on error
        """
        
        retVal = self.waitPacket()
        print("DBG: Versatile.getImage: retVal: %s" % str(retVal) )
        command, param = retVal
        if self.bVerbose: print("DBG: run_camera_subscriber: param: %s" % str(param))
        if param != None and len(param)> 0:
            data = param[0][0]
            if 1: # data.nType == Versatile.VersatileValue.nValueType_Image: # and command = Versatile.nCommandType_Value
                if self.bVerbose: print( "DBG: Versatile.getImage: image received" )
                im = data.convertToCvImage()
                if self.bVerbose: print( "DBG: Versatile.getImage: converted: shape: %s" % str(im.shape) )                
                return im
        return False
    # getImage - end
    
    def getBrodcastedImage( self, strBroadcasterID ):
        """
        get a (redundant) pair [Versatile Image, opencv image] from a broadcaster
        return False on error
        """
        retVal = self._send( Versatile.nCommandType_GetBroadcasted, str(strBroadcasterID) )
        if self.bVerbose: print("DBG: getImage: retVal: %s" % str(retVal) )
        if retVal == None:
            return False
        command, param = retVal
        if self.bVerbose: print("DBG: run_camera_subscriber: param: %s" % str(param))
        if param != None and len(param)> 0:
            data = param[0][0]
            if 1: # data.nType == Versatile.VersatileValue.nValueType_Image: # and command = Versatile.nCommandType_Value
                if self.bVerbose: print( "DBG: image received" )
                im = data.convertToCvImage()
                if self.bVerbose: print( "DBG: converted: shape: %s" % str(im.shape) )                
                return data,im
        return False
    # getBrodcastedImage - end
        
# class Versatile - end

def connectAndSend( strIP, strDataName, value = None ):
    v = Versatile()
    v.connect( strIP )
    if value == None:
        retVal = v.get( strDataName )
        #retVal = v.get( strDataName ) #test 2 calls in a raw
    else:
        retVal = v.set( strDataName, value )
    print( "connectAndSend: finished with value: %s" % str(retVal) )
    
def run_server(nPort=10001):
    print( "INF: versatile: starting server..." )
    v = Versatile(nPort=nPort)
    v.runServer()
    
def run_camera_subscriber( strServerIP, nPort=10001, bVerbose=False ):
    """
    duplicate from test_get_image
    """
    v = Versatile(nPort=nPort)
    v.connect( strServerIP )
    v.subscribeCamera( 0,Versatile.VersatileImage.WantedResolution.VGA,Versatile.VersatileImage.Format.PNG, 30 )

    nCptImage = 0
    nCptImageTotal = 0

    timeBegin = time.time()
    while 1:
        im = v.getImage()
        if not im is False:
                cv2.imshow("received", im)
                if bVerbose: print( "DBG: drawed" )
                nKey =  cv2.waitKey(1) & 0xFF
                bEnd = ( nKey == ord( 'q' ) or nKey == ord( 'Q' ) )
                if bEnd:
                    break

                nCptImage +=1
                nCptImageTotal += 1
                if nCptImage > 50:
                    print( "INF: fps: %5.1f (total image: %d)" % (nCptImage/(time.time()-timeBegin), nCptImageTotal) )
                    nCptImage = 0
                    timeBegin = time.time()

        else:
            print( "WRN: reception error...")
            
# run_camera_subscriber - end            
        
 
def autoTest():
    """
    autotest as a client
    """
    Versatile.VersatileImage.autoTest()
    # system( "python %s start_server" % sys.argv )
    pass # a bit complicated
    
    
    
if( __name__ == "__main__" ):
    #Versatile.VersatileImage_autoTest()
    
    def print_syntax():
        print( "" )
        print( "syntax: python %s remote_ip variable_name [value]" % sys.argv[0])
        print( "syntax: to start a server: python %s start_server"  % sys.argv[0] )
        print( "syntax: to subscribe images from a server: python %s remote_ip subscribe_camera"  % sys.argv[0] )
        print( "" )
        print( "To start a local test:\nshell 1: python %s start_server\nshell 2: python %s localhost myTime 12h34 & python %s localhost myTime" % (sys.argv[0],sys.argv[0],sys.argv[0]))
        exit( 0 )
        
    nPort = 10001
    # eat options
    i = 1
    while i < len(sys.argv):
        if sys.argv[i][0] == '-':
            if sys.argv[i][1] == 'p':
                nPort = int(sys.argv[i+1])
                print( "INF: changing to port %d" % (nPort) )
            del sys.argv[i]
            del sys.argv[i] # was the i+1
        else:
            i += 1
    if len(sys.argv) < 2:
        print_syntax()
    strIP = sys.argv[1]
    if strIP == "start_server":
        run_server(nPort=nPort)
        exit(1)    
        
    if len(sys.argv) < 3:
        print_syntax()
    
    strDataName = sys.argv[2]
    
    if strDataName == "subscribe_camera": # TODO: en cours de test: lancer un serveur d'un coté et subscribe_camera de l'autre
        run_camera_subscriber(strIP,nPort)
        exit(1)
        
    strValue = None
    if len(sys.argv)>3:
        strValue = sys.argv[3]
        
    retVal = connectAndSend( strIP, strDataName, strValue )
    print( "return:\n%s" % str(retVal) )

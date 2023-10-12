import socket
import threading
import struct
import time

def dumpHexaArray( anArray, nNbrByte = 1, bSigned = False ):
    """
    Dump an array
    """
    strTemp = "";
    for val in anArray:
        if( nNbrByte > 1 ):
            #for i in range( nNbrByte-1, -1, -1 ):
            for i in range( nNbrByte ):
                val8 = ( val >> (i*8) ) & 0xFF;
                strTemp += chr( val8 );
        else:
            strTemp += chr( val );
    return dumpHexa( strTemp );
# dumpHexaArray - end    

def dumpHexa( anArray ):
    """
    dump a string variable, even if containing binary
    return a string formated as an hexa editor panel with the hexa on left and text on right
    """
    # some cheap equivalent is: print repr(data)
    if( anArray == None ):
        return "WRN: debug.dumpHexa: Value is None!";
    #~ if( isinstance( anArray, np.ndarray ) ): # but requires to use np, pfff
        #~ anArray=anArray.tolist();
    strTxt = "dumpHexa data len: %d\n" % len( anArray );
    i = 0;
    strAsciiLine = "";
    strTxt += "%03d: " % i;
    while( i < len( anArray ) ):        
        strTxt += "%02x " % ord( anArray[i] );
        if( ord( anArray[i] ) >= 32 and ord( anArray[i] ) <= 127 ):
            strAsciiLine += "%s" % anArray[i];
        else:
            strAsciiLine += "_";
        i += 1;
        if( i % 8 == 0 ):
            strTxt += "  ";
        if( i % 16 == 0 ):
            strTxt += "  " + strAsciiLine + "\n";
            strTxt += "%03d: " % i;
            strAsciiLine = "";
    # while - end
    #~ print (i%16)
    if( (i%16) < 8):
        strTxt += "__ "*(8-(i%16)); # end of line
        strTxt += "  ";
        i = 8;
    strTxt += "__ "*(16-((i)%16)); # end of line
    if( i != 15 ):
        strTxt=strTxt[:-1]; # eat the last space!
    return strTxt + "     " + strAsciiLine + "\n";
# dumpHexa - end
#print( dumpHexa( "\t3213 Alexandre Mazel, happy happy man!\nYo!" ) );
#~ print( dumpHexa( "Alexandre"*1 ) );

def manageClientRequests( lient ):
    #handleNewClientArrival( client )
    print("INF: manageClientRequests")
    try:
        while 1:
            command, command_parameters = Versatile._waitPacket(client, bVerbose)
            if command == Versatile.nCommandType_EOC:
                client.close()
                break
            if bVerbose: print( "DBG: versatile.manageClientRequests: before handling command..." )
            valueToReturn = handleCommand( command, command_parameters, client )
            _send( Versatile.nCommandType_Value, None, valueToReturn, client )
    except socket.error as err:
        print( "ERR: when working with client, received error: %s" % err )
        client.close()
    handleClientLeft(client)
    
def runServer( nPort ):
    """
    run an infinite server
    """
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # DGRAM => UDP
    while True:
        try:
            socket_server.bind( ('0.0.0.0', nPort ) )
            break
        except OSError as err:
            print( "ERR: connection error: %s" % str(err) )
            print( "ERR: retrying in 2 sec..." )
            time.sleep( 2 )
            
    strLocalIP = socket_server.getsockname()[0]
    #~ strLocalIP = socket_server.gethostbyname("localhost")
    print( "INF: versatile.runServer: server ready at %s for client connection on port %s..." % (strLocalIP,nPort) )
    
    bMustStop = False
    nBufferSize = 1024
    
    
    """
Sur nao on recoit ca depuis touch designer:
receiving...
ip: ('192.168.4.2', 49206), msg: #bundle¦¦¦*¦¦0$/chan1,i
dumpHexa data len: 36
000: 23 62 75 6e 64 6c 65 00   e8 cf e3 2a 88 9f 30 24     #bundle____*__0$
016: 00 00 00 10 2f 63 68 61   6e 31 00 00 2c 69 00 00     ____/chan1__,i__
032: 00 00 00 00 __ __ __ __   __ __ __ __ __ __ __ __     ____

dumpHexa data len: 4
000: 88 9f 30 24 __ __ __ __   __ __ __ __ __ __ __ __     __0$

un autre:
ip: ('192.168.4.2', 49206), msg: #bundle¦¦¦R?¦O/chan1,i
dumpHexa data len: 36
000: 23 62 75 6e 64 6c 65 00   e8 cf e3 52 c9 8b c3 4f     #bundle____R___O
016: 00 00 00 10 2f 63 68 61   6e 31 00 00 2c 69 00 00     ____/chan1__,i__
032: 00 00 00 00 __ __ __ __   __ __ __ __ __ __ __ __     ____

dumpHexa data len: 4
000: c9 8b c3 4f __ __ __ __   __ __ __ __ __ __ __ __     ___O


    """
    while not bMustStop:
        #~ try:
        if 1:
            print("receiving...")
            msg, add = socket_server.recvfrom(nBufferSize)
            print("ip: %s, msg: %s" % (str(add),str(msg)))
            print(dumpHexa(msg))
            print(dumpHexa(msg[12:16]))
            val = struct.unpack("i", msg[12:16])[0]
            #~ print("val: " + str(val))
            #~ val = val/float(0x7FFFFFFF)
            val = ord(msg[12]) <<24 + ord(msg[13]) <<16 + ord(msg[14]) <<8 + ord(msg[15]);
            print("val: " + str(val))
            #~ print("float: %.2f" % val)
            
            #~ client, address = socket_server.accept()
            #~ print( "Versatile: client connect from %s" % str(address) )
            #manageClientRequests(client) # only one at a time !
            #~ threading.Thread( target=manageClientRequests, args=(client,) ).start() # the ',' after 'client' is important else it's not a tuple
            
        #~ except socket.error as err:
            #~ print( "ERR: when working with client, received error: %s" % err )
            #~ client.close()
            
        
        time.sleep(1)
        # flush all data
        socket_server.setblocking(0)
        while 1:
            try:
                msg, add = socket_server.recvfrom(nBufferSize)
            except: break
        # end of flush
        socket_server.setblocking(1)
                
    
    socket_server.close()
    print( "INF: versatile.runServer: stopped." )
        
runServer(8002)
   
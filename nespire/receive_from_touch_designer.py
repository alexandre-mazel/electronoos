import socket
import threading

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
            socket_server.bind( ('', nPort ) )
            break
        except OSError as err:
            print( "ERR: connection error: %s" % str(err) )
            print( "ERR: retrying in 2 sec..." )
            time.sleep( 2 )
    
    print( "INF: versatile.runServer: server ready for client connection on port %s..." % nPort )
    
    bMustStop = False
    while not bMustStop:
        try:
            socket_server.listen(5)
            client, address = socket_server.accept()
            print( "Versatile: client connect from %s" % str(address) )
            #manageClientRequests(client) # only one at a time !
            threading.Thread( target=manageClientRequests, args=(client,) ).start() # the ',' after 'client' is important else it's not a tuple
            
        except socket.error as err:
            print( "ERR: when working with client, received error: %s" % err )
            #~ client.close()
    
    socket_server.close()
    print( "INF: versatile.runServer: stopped." )
        
runServer(8002)
   
import os
import sys
import time

import serial # pip install pyserial

def listPorts():
    """
    list all open ports and print information on them.
    Return the first found
    """
    bVerbose = 1
    
    # chose an implementation, depending on os
    #~ if sys.platform == 'cli':
    #~ else:
    if os.name == 'nt':  # sys.platform == 'win32':
        from serial.tools.list_ports_windows import comports
    elif os.name == 'posix':
        from serial.tools.list_ports_posix import comports
    #~ elif os.name == 'java':
    else:
        raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))

    strFirstOpenPort = ""

    iterator = sorted(comports())
    # list them
    for n, (port, desc, hwid) in enumerate(iterator, 1):
        if strFirstOpenPort == "": 
            strFirstOpenPort = port
        sys.stdout.write("listPorts: open port: {:20}\n".format(port))
        if bVerbose:
            sys.stdout.write("    desc: {}\n".format(desc))
            sys.stdout.write("    hwid: {}\n".format(hwid))
            
    return strFirstOpenPort
        
        
def monitorPort(strPortName, nBaudRate=9600):
    """
    return 2 if user want to stop
    """
    
    retVal = 1
    
    try:
        ser = serial.Serial(strPortName) # pb: ca gele tant que rien n'est recu... c'est dommage...
        
    except BaseException as err: # including KeyboardInterrupt
        print("ERR: monitorPort (1): %s" % str(err) )
        return 1
    
    """
    strPortName,
        baudrate=9600, 
    timeout=1,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
    """
    if nBaudRate != 9600: # default
        ser.baudrate = nBaudRate

    try:
        print("INF: %s is open: %s at %s" % (ser.name,ser.is_open,nBaudRate) )
        #~ for i in range(100):
        prevPrint = ""
        
        # tempo, send a trace to debug angle
        while 1:
            buf = ser.readline()
            buf = str(buf)
            buf = buf.replace("\n","")
            buf = buf.replace("\r","")
            buf = buf.replace("\\r\\n","")
            buf = buf.replace("b'","")
            if buf[-1]== "'": buf = buf[:-1]
            #~ buf = buf.decode(encoding='utf-8', errors='strict')
            if buf != prevPrint:
                prevPrint = buf
                print("buf: " + buf)
            ser.write("print 2".encode())
    except BaseException as err: # including KeyboardInterrupt
        print("ERR: monitorPort (2): %s" % str(err) )
        if "ClearCommError" not in str(err):
            retVal = 2
    ser.close()
    print("INF: monitorPort: exiting with code %s" % str(retVal) )
    return retVal

if __name__ == "__main__":
    print("Command line syntaxe: scriptname [<PORT_NAME>] [baud, default is 57600]")
    print("")
    #~ listPorts()
    strPortName = '/dev/ttyUSB0'
    strPortName = 'COM7'
    strPortName = 'COM6'
    strPortName = 'COM8'
    nBaudRate = 9600
    nBaudRate = 57600
    #~ nBaudRate = 115200
    
    strPortNameAutodetect = listPorts()
    
    if len(sys.argv) > 1:
        strPortName = sys.argv[1]
        
    if len(sys.argv) > 1:
        nBaudRate = int(sys.argv[2])

            
    if 0:
        print("using autodetected port: %s" % strPortNameAutodetect )
        strPortName = strPortNameAutodetect
        
    print("\nINF: Connecting to %s (baud: %s)" % (strPortName,nBaudRate) )
    while 2 != monitorPort(strPortName,nBaudRate):
        time.sleep(1.)
        print("Reconnecting...")
    print("INF: script finished...")

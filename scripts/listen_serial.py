import os
import sys

import serial # pip install pyserial

def listPorts():
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


    iterator = sorted(comports())
    # list them
    for n, (port, desc, hwid) in enumerate(iterator, 1):
        sys.stdout.write("{:20}\n".format(port))
        if bVerbose:
            sys.stdout.write("    desc: {}\n".format(desc))
            sys.stdout.write("    hwid: {}\n".format(hwid))
        
        
def monitorPort(strPortName):
    ser = serial.Serial(strPortName)
    print("INF: %s is open: %s" % (ser.name,ser.is_open) )

    buf = ser.read(100)
    print(buf)
    ser.close()

listPorts()
strPortName = '/dev/ttyUSB0'
strPortName = 'COM7'
monitorPort(strPortName)

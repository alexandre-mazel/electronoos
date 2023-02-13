import os
import sys
import time

strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import nettools

def getTemperatureFrom1wire(strDeviceID):
    """
    open w1 devices and extract temperature, return it in degree Celsius
    find /sys/bus/w1/devices/ -name "28-*" -exec cat {}/w1_slave \; | grep "t=" | awk -F "t=" '{print $2/1000}'

    """
    f = open("/sys/bus/w1/devices/%s/w1_slave" % strDeviceID,"rt")
    lines = f.readlines()
    print("lines: %s" % str(lines))
    if len(lines)>0:
        t = lines[-1].split("t=")[-1]
        t = int(t)/1000.
    else:
        t = -127
    return t
    
    
def run_loop_send(strDeviceID):
    while 1:
        t = getTemperatureFrom1wire(strDeviceID)
        if t > -127:
            nettools. sendDataToEngServer("temp", t)
        time.sleep(5*60)
        
if __name__ == "__main__":
    run_loop_send("28-3c09f64897a2")
    
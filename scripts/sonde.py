import os
import sys
import time

"""
copy from pimeteo
scp pi@192.168.0.38:/home/pi/save/local_temperature.txt C:\Users\alexa\dev\git\electronoos\meteo\pimeteo_local_temperature.txt
ou
scp pi@192.168.0.38:/home/pi/save/local_temperature.txt C:\save\pimeteo_local_temperature.txt
"""


strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools
import nettools

def getTemperatureFrom1wire(strDeviceID):
    """
    open w1 devices and extract temperature, return it in degree Celsius
    find /sys/bus/w1/devices/ -name "28-*" -exec cat {}/w1_slave \; | grep "t=" | awk -F "t=" '{print $2/1000}'

    """
    try:    
        f = open("/sys/bus/w1/devices/%s/w1_slave" % strDeviceID,"rt")
        lines = f.readlines()
        print("lines: %s" % str(lines))
        if len(lines)>0:
            t = lines[-1].split("t=")[-1]
            t = int(t)/1000.
    #        t -= 1.5 # seems to be a bit higher than real
        else:
            t = -127
    except FileNotFoundError:
        t = -127
    return t
    
    
def run_loop_send(strDeviceID):
    while 1:
        for i in range(10):
            t = getTemperatureFrom1wire(strDeviceID)
            if t > -127:
                if 1:
                    # save in local file
                    timestamp = misctools.getTimeStamp()
                    if os.name == "nt":
                        dest = "c:/save/office_temperature.txt"
                    else:
                        #~ dest = os.path.expanduser("~/save/office_temperature.txt")
                        dest = "/home/pi/save/local_temperature.txt" # here we want to save there, even if running as root
                    
                    f = open(dest,"a+")
                    f.write("%s: %s: %.1f\n" % (timestamp,"various",t) )
                    f.close()
                    
                nettools.sendDataToEngServer("temp", t)
                break
            else:
                time.sleep(2)
        time.sleep(5*60)
        
if __name__ == "__main__":
    run_loop_send("28-3c09f64897a2")
    

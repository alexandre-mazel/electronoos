#!/usr/bin/python3
# coding: utf-8
import os
import time
import datetime

def getTimeStamp():
    """

    # REM: linux command:
    # timedatectl list-timezones: list all timezones
    # sudo timedatectl set-timezone Europe/Paris => set paris
    """
    datetimeObject = datetime.datetime.now()
    strTimeStamp = datetimeObject.strftime( "%Y/%m/%d: %Hh%Mm%Ss" )
    return strTimeStamp


def log(strTxt):
    file = open("/home/xenia/background_task.log", "at")
    strOut = "%s: INF: %s\n" % (getTimeStamp(), strTxt)
    print( strOut )
    file.write( strOut )
    file.close()
    
def runCommandGetResults( strCommand ):
    strFilename = "/tmp/" + str(time.time())
    os.system(strCommand + " > " + strFilename )
    f = open(strFilename, "rt")
    buf = f.read()
    f.close()
    os.remove(strFilename)
    return buf
    
def getTemperatures( buf ):
    """
    parse lines and return first temperature found each line
    """
    lines = buf.split("\n")
    #~ print("lines: " + str(lines) )
    aT = []
    for line in lines:
        #~ print(line)
        i = 0
        while i < len(line)-1:
            if ord(line[i]) == 176 and line[i+1] == 'C': # 176: symbol degrees on this system
                j = i-1
                while (line[j] >= '0' and line[j] <= '9') or line[j] == '.':
                    j -= 1
                    if j < 0:
                        break
                t = float(line[j:i])
                print("t: %s => %f" % (line[j:i],t) )
                aT.append(t)
                break # or continue if all temperatures in each lines
            i += 1
        # while - end
        
    return aT
# getTemperatures - end    

def changeFanSpeed(rSpeedCpu, rSpeedBoard):
    """
    rFanSpeed in 0..1
    """
    print("INF: changeFanSpeed(%5.2f,%5.2f)" % (rSpeedCpu, rSpeedBoard) )
    nMax = 255
    nSpeedFanGroupCpu = int(rSpeedCpu*nMax)
    nSpeedFanGroupBoard = int(rSpeedBoard*nMax)
    
    idxGroupCpu = [2,3]
    idxGroupBoard = [6]
    for idx in idxGroupCpu:
        os.system( "echo 1 >/sys/class/hwmon/hwmon2/pwm%d_enable" % idx )
        os.system( "echo %d > /sys/class/hwmon/hwmon2/pwm%d" % (nSpeedFanGroupCpu, idx) )

    for idx in idxGroupBoard:
        os.system( "echo 1 >/sys/class/hwmon/hwmon2/pwm%d_enable" % idx )
        os.system( "echo %d > /sys/class/hwmon/hwmon2/pwm%d" % (nSpeedFanGroupBoard, idx) )
        
def getGoodSpeed(rTemp):
    """
    """
    speedrules = [
                            [44,0.1],
                            [46,0.2],
                            [50,0.3],
                            [60,0.4],
                            [65,0.6],
                            [75,0.8],
                            [80,1.],
                    ]
    speed = 0
    for p in speedrules:
        t,s=p
        if rTemp<t:
            break
        speed = s
    return speed
    
global_rPrevCpu = 0
global_rPrevBoard = 0

def check_temp():
    buf = runCommandGetResults( "sensors coretemp-isa-0000" )
    #~ print(buf)
    t = getTemperatures(buf)
    rCpu = max(t)
    print("INF: max cpu: %5.1fdeg" % rCpu )
    buf = runCommandGetResults( "sensors pch_cannonlake-virtual-0")
    #~ print(buf)
    t = getTemperatures(buf)
    rBoard = max(t)
    print("INF: max board: %5.1fdeg" % rBoard )

    
    global global_rPrevCpu
    global global_rPrevBoard
    if global_rPrevCpu == rCpu and global_rPrevBoard == rBoard:
        return
        
    global_rPrevCpu = rCpu
    global_rPrevBoard = rBoard
    
    speedCpu = getGoodSpeed(rCpu)
    speedBoard = getGoodSpeed(rBoard-10) # this temp seems not to be critical

    
    log( "%sdeg, %sdeg => speed at %5.2f,%5.2f" % (rCpu,rBoard,speedCpu,speedBoard) )
    
    changeFanSpeed(speedCpu,speedBoard)
    
# check_temp - end

def ping_other():
    pass

time_lastUsefull = time.time()
def auto_off():
    global time_lastUsefull
    nNbrConnected = int(runCommandGetResults("who | wc -l"))
    rLoad = float(runCommandGetResults("uptime | cut -d ',' -f 4"))
    print("INF: nNbrConnected: %d, load: %5.2f" % (nNbrConnected,rLoad) )
    if nNbrConnected > 0 or rLoad > 0.1:
        time_lastUsefull = time.time()
    else:
        if time.time() - time_lastUsefull > 60*10:
            log("INF: no connection, shutting down (nNbrConnected: %d, load: %5.4f)..." % (nNbrConnected,rLoad) )
            os.system( "halt -p")
    
    
def main():
    log("background_task: starting")
    while 1:
        check_temp()
        ping_other()
        try: auto_off()
        except BaseException as err: log( "ERR: auto_off: %s" % str(err))
        time.sleep(60)


main()
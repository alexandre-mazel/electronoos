import naoqi
import time

mot = naoqi.ALProxy("ALMotion", "localhost", 9559)
mem = naoqi.ALProxy("ALMemory", "localhost", 9559)

rAngleCommand = 0.4
strJointName = "HipPitch"
strJointName = "HeadYaw"
while 1:
    rAngleInit = mem.getData("Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName)
    print("rAngleInit: %s" % rAngleInit)
    rAngleCommand = -rAngleCommand
    print( "%s: start - moveto %s\n" % (time.time(),rAngleCommand) )
    timeBegin = time.time()
    mot.setAngles(strJointName, rAngleCommand, 0.3)
    
    if 0:
        # draw all values
        while time.time()-timeBegin < 2:
            rAngle = mem.getData("Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName)
            print("%s: %f" % (time.time(),rAngle) )
            time.sleep(0.02)
            
    if 1:
        # draw only time to move and time to arrive
        bStartMove = False
        while 1:
            rAngle = mem.getData("Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName)
            if not bStartMove:
                if abs(rAngle - rAngleCommand)<0.02:
                    bStartMove = True
                    print("Start to move: %5.3fs (angle: %5.3f)" % (time.time()-timeBegin,rAngle))
                    timeStartMove = time.time()
            else:
                if abs(rAngle - rAngleCommand)<0.02:
                    print("~complete: total: %5.3fs, move: %5.3fs" % (time.time()-timeBegin,time.time()-timeStartMove))
                    break

            time.sleep(0.0001)            
    time.sleep(2)
    
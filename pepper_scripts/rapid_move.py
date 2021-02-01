import naoqi
import time

mot = naoqi.ALProxy("ALMotion", "localhost", 9559)
mem = naoqi.ALProxy("ALMemory", "localhost", 9559)

rAngleCommand = 0.1
strJointName = "HipPitch"

rAngleCommand = 0.4
strJointName = "HeadYaw"
while 1:
    rAngleInit = mem.getData("Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName)
    print("rAngleInit: %5.5f" % rAngleInit)
    
    rAngleCommand = -rAngleCommand
    print( "%s: start - moveto %s\n" % (time.time(),rAngleCommand) )
    timeBegin = time.time()
    
    rThresholdAngleArrived = 0.02
    if 1:
        #~ rThresholdAngleArrived = 0.2 # less precise when using interpolation
        mot.post.angleInterpolationWithSpeed(strJointName, rAngleCommand, 0.4) # time to start: headyaw ~ 0.0030s whatever the fraction # however it seems far more at usage, weird...
    else:
        mot.setAngles(strJointName, rAngleCommand, 0.4)    # time to start: headyaw ~ 0.0020s whatever the fraction
    
    if 0:
        # draw all values
        while time.time()-timeBegin < 2:
            rAngle = mem.getData("Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName)
            print("%s: %5.5f" % (time.time(),rAngle) )
            time.sleep(0.02)
            
    if 1:
        # draw only time to move and time to arrive
        bStartMove = False
        while 1:
            rAngle = mem.getData("Device/SubDeviceList/%s/Position/Sensor/Value" % strJointName)
            #~ print("%s: %f" % (time.time(),rAngle) )
            if not bStartMove:
                if abs(rAngle - rAngleInit)<0.01:
                    bStartMove = True
                    print("Start to move: %5.4fs (angle: %5.5f)" % (time.time()-timeBegin,rAngle))
                    timeStartMove = time.time()
            else:
                if abs(rAngle - rAngleCommand)<rThresholdAngleArrived:
                    print("~complete: total: %5.4fs, move: %5.4fs\n" % (time.time()-timeBegin,time.time()-timeStartMove))
                    break

            time.sleep(0.0001)            
    time.sleep(2)
    
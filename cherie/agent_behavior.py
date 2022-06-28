"""
This file is part of CHERIE: Care Human Extended Real-life Interaction Experimentation.

Pepper consumption:

Full Loaded Battery, running Cherie:

stiff full leds: 73.5w
just one leg stiff full leds: 69.7w
rest full leds: 63.4w
rest no leds, running Cherie: 61.9w
rest no leds naoqi idle: 61.0w

# battery vraiment fully charged
rest full leds: 63.4w
rest no leds, running Cherie: 38w


scp -r C:\Users\alexa\dev\git\electronoos\cherie\sound* nao@192.168.0.15:/home/nao/
"""

import os
import random
import sys
import time
    
try:
    sys.path.append("../../electronoos/alex_pytools")
    import face_detector_cv3
    import misctools
    import cv2_tools
except:
    print("INF: Trying robot path")
    sys.path.append("/home/nao/.local/lib/python2.7/site-packages/electronoos/alex_pytools")  

import naoqi
import sound_player

class AgentBehavior:
    """
    human_manager stores cold facts, here we will play with them
    """
    
    def __init__( self ):
        self.motion = naoqi.ALProxy( "ALMotion", "localhost", 9559 )
        self.listInterestedSounds = []
        for i in range(10):
            self.listInterestedSounds.append("/home/nao/sounds/interested_sound__%04d.wav" % i)
        
    def playSmallSounds(self):
        rSoundVolume = 0.2
        idx = random.randint(0,len(self.listInterestedSounds)-1)
        sound_player.soundPlayer.playFile(self.listInterestedSounds[idx], bWaitEnd=False, rSoundVolume=rSoundVolume)

    def moveHands(self):
        strHand = "LHand"
        if random.random() > 0.5:
            strHand = "RHand"
        rIncMove = (random.random()*0.5)-0.1
        rTimeMove = random.random()*0.3+0.2
        self.motion.post.angleInterpolation(strHand,[rIncMove,-rIncMove],[rTimeMove,rTimeMove*2],False)
        
    def reactToLookAt( self, facepose,humaninfo ):
        self.playSmallSounds()
        
    def reactToNear( self, facepose,humaninfo ):
        if time.time()-humaninfo.timeLastReactToNear>10:
            humaninfo.timeLastReactToNear = time.time()
            self.moveHands()
        
    def startInteraction( self, facepose,humaninfo ):
        strJoint = "HipRoll"
        rIncMove = 0.2
        rTimeMove = 0.6
        self.motion.angleInterpolation( strJoint, [rIncMove,-rIncMove,0], [rTimeMove,rTimeMove*2,rTimeMove*3], True)
        

# class AgentBehavior - end

agentBehavior = AgentBehavior()


def prepareSound():
    import sound_processing
    sound_processing.autocut("rough\interested_sound.wav", bNormalise=1,bAddFadeInOut=1,bPlaySound=1)
    
if 0:
    prepareSound()
    exit(1)
    
def autotest():
    pass
    #~ agentBehavior.playSmallSounds()
    #~ agentBehavior.moveHands()
    #~ agentBehavior.startInteraction(None,None)



if __name__ == "__main__":
    autotest()
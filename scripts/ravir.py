# coding: cp1252

"""
Breath engine for RAVIR project
# copy manually all breathing to Pepper:
scp -r C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/breath* nao@192.168.0.:/home/nao/
scp -r C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut* nao@192.168.0.:/home/nao/
scp d:/Python38-32/Lib/site-packages/opensimplex/*.py nao@192.168.0.:/home/nao/.local/lib/python2.7/site-packages/

scp -pw nao C:/Users/amazel/dev/git/electronoos/scripts/rav*.py nao@192.168.1.211:/home/nao/dev/git/electronoos/scripts/

Currently I'm inserting a silence at the beginning of each breath:
sound_processing:
        rTimeAdded = 0.1
        strPath = "/tmp2/brea/selected_intake/"
        strPath = "/home/nao/breath/selected_intake/"
        insertSilenceInFolder(strPath, rTimeAdded)
        insertSilenceInFolder("/home/nao/breath/selected_outtake/", rTimeAdded)

So we wait a bit for the body motion reaction
"""

import os
import sys
strLocalPath = os.path.dirname(sys.modules[__name__].__file__)
if strLocalPath == "": strLocalPath = './'
sys.path.append(strLocalPath+"/../alex_pytools/")
import misctools
import noise
import sound_player
import wav

import math
import random
import time


class Breather:
    kStateIdle = 0
    kStateIn = 1 # inspiration
    kStateOut = 2 # expiration
    kStateInBeforeSpeak = 3
    kStateSpeak = 4
    #~ kStateListen = 5 #not a real state, just a boolean added to the machine
    kStatePause = 10 # do nothing, just stand
    
    def __init__( self ):
        
        # physical specification
        self.rSpeakDurationWhenFull = 4. # in sec

        # we naturally  doesn't use our full capacity
        self.rNormalMax = 0.7
        self.rNormalMin = 0.2
        
        # La frequence respiratoire normale d'un adulte se situe entre 12 et 20. ici on va se mettre a 18: petit adulte
        # enfant de 8 ans => 1 cycle en 3 sec
        
        #~ rCoefAnatomic = 1. # on va se baser sur un adulte moyen
        rPeriod = 60/12
        rNormalAmplitude = self.rNormalMax-self.rNormalMin
        self.rNormalInPerSec = rNormalAmplitude / ( (2*rPeriod)/5 )
        self.rNormalOutPerSec = rNormalAmplitude / ( (3*rPeriod)/5 )
        
        self.rPreSpeakInRatio = 2.5
        
        print("rPeriod: %s" % rPeriod)
        print("self.rNormalInPerSec: %s" % self.rNormalInPerSec)
        print("self.rNormalOutPerSec: %s" % self.rNormalOutPerSec)

        
        self.rFullness = 0. # current fullness of limb from 0 to 1
        self.rTargetIn = self.rNormalMax
        self.nState = Breather.kStateIdle
        self.timeLastUpdate = time.time()
        
        self.rExcitationRate = 1. # va modifier la quantite d'air circulant par seconde, 1: normal, 0.5: tres cool, 2: excite, 3: tres excite 
        self.bReceiveExcitationFromExternal = False
        
        self.rTimeIdle = 0.
        self.rTimeSpeak = 0.
        
        self.strFilenameToSay = "" # if set => want to speak
        
        self.motion = None
        
        self.idMoveHead = -1
        
        self.bListening = False
        
        if os.name != "nt":
            import naoqi
            self.motion = naoqi.ALProxy("ALMotion", "localhost", 9559)
            self.leds = naoqi.ALProxy("ALLeds", "localhost", 9559)
            self.astrChain = ["HipPitch","LShoulderPitch","RShoulderPitch"]
            
            self.rAmp = 0.2
            self.rCoefArmAmp = 0.5

            self.rHeadDelay = 0.6
            self.rHeadPos = self.rAmp*self.rCoefArmAmp*0.1*1.5
            self.rOffsetHip = -0.0
            
            self.wake()
        else:
            self.leds = False
            
            
        
    def loadBreathIn( self, strBreathSamplesPath ):
        """
        load all soundname and their duration
        """
        self.aBreathIn = []  # a list of pair [wavfilename, duration]
        
        for f in sorted(  os.listdir(strBreathSamplesPath) ):
            af = strBreathSamplesPath + f
            w = wav.Wav(af,bLoadData=False)
            self.aBreathIn.append([af,w.getDuration()] )
            
        print("INF: LoadBreathIn: load finished")
        
    def loadBreathOut( self, strBreathSamplesPath ):
        """
        """
        self.aBreathOut = []  # a list of pair [wavfilename, duration]
        
        for f in sorted(  os.listdir(strBreathSamplesPath) ):
            af = strBreathSamplesPath + f
            w = wav.Wav(af,bLoadData=False)
            self.aBreathOut.append([af,w.getDuration()] )
            
        print("INF: LoadBreathOut: load finished")    
        
    def playBreath( self, listSoundAndDuration, rApproxDuration ):
        """
        Find a sample equal or slightly shorter than rApproxDuration and play it
        """
        sound_player.soundPlayer.stopAll()

        nIdxBest = -1
        rBestApprox = -1
        i = 0
        while i < len( listSoundAndDuration ):
            af,r = listSoundAndDuration[i]
            if r <= rApproxDuration and r > rBestApprox:
                rBestApprox = r
                nIdxBest = i
            i += 1
        f = listSoundAndDuration[nIdxBest][0]
        
        rSoundVolume = 0.18 * self.rExcitationRate
        
        if self.nState == Breather.kStateInBeforeSpeak:
            rSoundVolume *= self.rPreSpeakInRatio
            
        if rSoundVolume < 0.1: rSoundVolume = 0.1
        if rSoundVolume > 0.4: rSoundVolume = 0.4
        

        
        print("INF: Play %s, vol: %5.1f" % (f.split('/')[-1],rSoundVolume) )
        
        sound_player.soundPlayer.playFile(f, bWaitEnd=False, rSoundVolume=rSoundVolume)

    
    def wake(self):
        if self.motion:
            self.motion.wakeUp()
            self.motion.angleInterpolationWithSpeed("KneePitch",-0.0659611225, 0.05)
        
    def updateBodyPosture(self, rFullness = -1):
        
        if rFullness == -1: rFullness = self.rFullness
        
        if self.motion != None:
            #self.motion.setAngles("HeadYaw",self.rFullness,0.5)
            #~ ( self.astrChain, [self.rAmp*0.1+self.rOffsetHip,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
            rMin = -self.rAmp*0.2
            rMax = self.rAmp*0.2
            if rFullness > 1.6:
                self.rFullness = 1.6 # we could have lock it to 1, but more is fine also (let's track some bugs) # seen once at 3.53 and the robot hadn't fall!
            rPos = rMin+self.rFullness*(rMax-rMin)
            self.motion.setAngles(self.astrChain,[rPos+self.rOffsetHip,(math.pi/2)+rPos*self.rCoefArmAmp,(math.pi/2)+rPos*self.rCoefArmAmp],0.6)

    def updateHeadTalk(self):
        if self.motion != None:
            rInc = 0.02+random.random()*0.2
            self.motion.setAngles("HeadPitch", rInc, random.random()/15. )

    def updateHeadListen(self):
        if self.motion != None:
            rInc = 0.02+random.random()*0.1
            self.motion.setAngles("HeadPitch", rInc, random.random()/45. )            
           
    def setHeadIdleLook( self, listHeadOrientation, ratioTimeFirst ):
        self.listHeadOrientation = listHeadOrientation
        self.ratioTimeFirst = ratioTimeFirst
        self.lastHeadMove = time.time()
        
    def updateHeadLook( self, nForcedAngle = -1):
        """
        nForcedAngle: force to look at this direction NOW
        """
        if not self.motion: return
        if time.time() - self.lastHeadMove > 3 or nForcedAngle != -1:
            if random.random()<0.7 and time.time() - self.lastHeadMove < 8 and nForcedAngle == -1: # proba de pas bouger
                return
            self.lastHeadMove = time.time()
            if nForcedAngle == -1:
                if random.random()<self.ratioTimeFirst:
                    idx = 0
                else:
                    idx = random.randint(0,len(self.listHeadOrientation)-2)
                    idx = idx + 1
                rSpeed = 0.01+random.random()*0.2
            else:
                idx = nForcedAngle
                rSpeed = 0.2
            headPos = self.listHeadOrientation[idx]
            try:
                self.motion.killTask(self.idMoveHead)
            except BaseException as err:
                print("WRN: stopping task %d failed: %s" % (self.idMoveHead,err) )
            self.idMoveHead=self.motion.post.angleInterpolationWithSpeed("Head",headPos,rSpeed)
                
            
    def update( self, nForceNewState = None ):
        rTimeSinceLastUpdate = time.time() - self.timeLastUpdate
        self.timeLastUpdate = time.time()
        
        #~ print("\n%5.2fs: DBG: Breather.update: state: %s, rFullness: %4.2f, rExcitation: %5.1f, self.rTimeIdle: %5.2f, self.rTimeSpeak: %5.2f, rTimeSinceLastUpdate: %5.2f" % (time.time(),self.nState,self.rFullness,self.rExcitationRate, self.rTimeIdle,self.rTimeSpeak,rTimeSinceLastUpdate) )
        
        nPrevState = self.nState
        
        if nForceNewState != None:
            self.nState = nForceNewState
            
        if self.nState != Breather.kStatePause:        
            # update fullness
            if self.nState == Breather.kStateIn:
                self.rFullness += self.rNormalInPerSec*self.rExcitationRate*rTimeSinceLastUpdate

            if self.nState == Breather.kStateInBeforeSpeak:
                self.rFullness += self.rNormalInPerSec*self.rExcitationRate*rTimeSinceLastUpdate*self.rPreSpeakInRatio
                
            if self.nState == Breather.kStateOut:
                self.rFullness -= self.rNormalOutPerSec*self.rExcitationRate*rTimeSinceLastUpdate
                
            if self.nState == Breather.kStateIdle:
                self.rTimeIdle -= rTimeSinceLastUpdate
                if self.rTimeIdle < 0:
                    self.nState = Breather.kStateIn

            if self.nState == Breather.kStateSpeak:
                self.rTimeSpeak -= rTimeSinceLastUpdate
                self.rFullness -= self.rExcitationRate*rTimeSinceLastUpdate / self.rSpeakDurationWhenFull
                if self.rTimeSpeak < 0:
                    self.nState = Breather.kStateIdle
                    
            self.updateBodyPosture()
            
            if self.nState == Breather.kStateSpeak:
                self.updateHeadTalk()
            elif self.nState != Breather.kStateInBeforeSpeak and not self.bListening:
                self.updateHeadLook()
                
            if self.bListening:
                self.updateHeadListen()
                    
                    
            if self.strFilenameToSay != "" and self.nState != self.kStateSpeak:
                self.updateHeadLook(0)
                if self.rFullnessToSay < self.rFullness:
                    self.nState = Breather.kStateSpeak
                else:
                    self.nState = Breather.kStateInBeforeSpeak

            
            if self.nState != Breather.kStateSpeak and self.nState != Breather.kStateInBeforeSpeak:
                # automatic change of in/out
                if self.nState != Breather.kStateIn and (self.rFullness <= self.rNormalMin or (self.rFullness <= self.rNormalMin+0.2 and random.random()>0.93) ):
                    self.nState = Breather.kStateIdle
                    
                if self.nState != Breather.kStateOut  and self.rFullness >= self.rTargetIn:
                    self.nState = Breather.kStateOut
            
        if self.nState != nPrevState:
            
            ######################################
            # change of state
            ######################################
            
            if nPrevState == Breather.kStatePause:
                self.wake()
            
            if self.nState == Breather.kStateIn or self.nState == Breather.kStateInBeforeSpeak:
                self.rTargetIn = self.rNormalMax
                if self.strFilenameToSay != "":
                    self.rTargetIn = self.rFullnessToSay +0.3 # add margin to prevent having to full respi at the end
                    if self.rTargetIn > 1.: self.rTargetIn = 1.
                else:
                    if  random.random()>0.95:
                        print( "INF: full respi" )
                        self.rTargetIn = 1. 
                rTimeEstim = ( self.rTargetIn - self.rFullness) / (self.rNormalInPerSec*self.rExcitationRate)
                if self.nState == Breather.kStateInBeforeSpeak:
                    rTimeEstim /= self.rPreSpeakInRatio
                #~ if self.motion != None:
                    #~ self.motion.stopMove()
                    #~ self.motion.post.angleInterpolation( self.astrChain, [self.rAmp*0.1+self.rOffsetHip,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)+self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
                self.playBreath( self.aBreathIn, rTimeEstim )

                
            if self.nState == Breather.kStateOut:
                rTimeEstim = (self.rFullness-self.rNormalMin) / (self.rNormalOutPerSec*self.rExcitationRate)
                #~ if self.motion != None:
                    #~ self.motion.stopMove()
                    #~ self.motion.post.angleInterpolation( self.astrChain, [-self.rAmp*0.1+self.rOffsetHip,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )
                self.playBreath( self.aBreathOut, rTimeEstim )  
                
            if self.nState == Breather.kStateIdle:
                self.rTimeIdle = random.random() # jusqu'a 1sec d'idle
                if self.leds: self.leds.post.fadeRGB("FaceLeds", 0x202020, 0.5)
                if nPrevState == Breather.kStateSpeak:
                    self.rTimeIdle += 0.5

            if self.nState == Breather.kStateSpeak:
                sound_player.soundPlayer.stopAll()
                if self.leds: self.leds.fadeRGB("FaceLeds", 0x0000FF, 0.00)
                sound_player.soundPlayer.playFile(self.strFilenameToSay, bWaitEnd=False)
                #~ if self.motion != None:
                    #~ rTimeEstim = self.rTimeSpeak
                    #~ self.motion.stopMove()
                    #~ self.motion.post.angleInterpolation( self.astrChain, [-self.rAmp*0.1+self.rOffsetHip,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1,(math.pi/2)-self.rAmp*self.rCoefArmAmp*0.1], rTimeEstim-0.15, True )

                self.strFilenameToSay = ""
                
            if self.nState == Breather.kStatePause:
                # reset state
                sound_player.soundPlayer.stopAll()
                self.updateHeadLook(0)
                self.updateBodyPosture(1.) # ou rest ?
                #~ self.motion.rest()
            
            self.rExcitationRate += noise.getSimplexNoise(time.time())/100. # random.random()*3 (change trop violemment)
            if self.rExcitationRate < 0.1: self.rExcitationRate = 0.1
            
            print("%5.2fs: INF: Breather.update: new state: %s, rFullness: %4.2f, rExcitation: %5.1f" % (time.time(),self.nState,self.rFullness,self.rExcitationRate) )
        
            if self.bReceiveExcitationFromExternal:
                if self.rExcitationRate >= 0.9:
                    self.rExcitationRate -= 0.02 # will mess  the nice simplex noise "average tends to 0"
                else:
                    self.bReceiveExcitationFromExternal = False
                
    def isSpeaking( self ):
        return self.strFilenameToSay != "" or self.nState == Breather.kStateSpeak
        
    def sayTts( self, strText ):
        import tts
        if tts.tts.isLoaded(): tts.tts.load()
        #~ self.strMessageToSay = txt
        self.strFilenameToSay, self.rTimeSpeak = tts.tts.sayToFile( strText )
        self.rFullnessToSay = self.rTimeSpeak / self.rSpeakDurationWhenFull
        print("INF: Breather.sayTts %s: rTimeSpeak: %5.2fs, rFullnessToSay: %5.2f" % (strText,self.rTimeSpeak,self.rFullnessToSay) )
        
    def sayFile( self, filename ):
        #~ self.strMessageToSay = txt
        self.strFilenameToSay = filename
        w = wav.Wav(filename,bLoadData=False)
        self.rTimeSpeak = w.getDuration()
        self.rFullnessToSay = self.rTimeSpeak / self.rSpeakDurationWhenFull
        print("INF: Breather.sayFile %s: rTimeSpeak: %5.2fs, rFullnessToSay: %5.2f" % (filename,self.rTimeSpeak,self.rFullnessToSay) )
                
    def increaseExcitation( self, rInc ):
        print("INF: adding external excitation: %5.1f" % rInc)
        self.rExcitationRate += rInc
        self.bReceiveExcitationFromExternal = True
        
        
    def isPaused(self):
        return self.nState == Breather.kStatePause
        
    def setPaused(self, bNewState):
        print("INF: Breather.setPaused: %d" % (bNewState) )
        if bNewState:
            self.update(Breather.kStatePause)
        else:
            self.update(Breather.kStateIdle)
            
            
    def setListening(self, bNewState):
        print("INF: Breather.setListening: %d => %d" % (breather.bListening,bNewState) )
        if bNewState:
            self.updateHeadLook(0)
        breather.bListening = bNewState
        
# class Breather - end


breather = Breather()

def init():
    """
    load, return talkpath,mem
    """
    if os.name == "nt":
        breather.loadBreathIn( "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/breath/selected_intake/")
        breather.loadBreathOut( "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/breath/selected_outtake/")
        strTalkPath = "C:/Users/amazel/perso/docs/2020-10-10_-_Ravir/cut/rec2/"
        mem = None
    else:
        breather.loadBreathIn( "/home/nao/breath/selected_intake/")
        breather.loadBreathOut( "/home/nao/breath/selected_outtake/")
        strTalkPath = "/home/nao/cut/rec2/"
        import naoqi
        mem = naoqi.ALProxy("ALMemory", "localhost", 9559)
        
    return strTalkPath,mem
    
def loadDialogs():
    #msgs = ["s053__ah_merci_je_comprends_mieux_maintenant_je_suis_content_d_avoir_appris_seul_p1","s053__ah_merci_je_comprends_mieux_maintenant_je_suis_content_d_avoir_appris_seul_p2"]

    msgs = []
    msgs.append("s005__j_ai_remarque_qu_il_y_a_moins_de_monde_la_nuit_dans_les_rues_par_rapport_a_l_age")
    msgs.append("s006__ca_me_gene_je_mens")
    msgs.append("s007__j_ai_l_impression_de_ne_pas_savoir_quoi_faire_je_me_sens_en_minutes")
    msgs.append("s008__je_ne_comprends_pas_pourquoi_il_y_a_une_difference_entre_le_jour_et_la_nuit_c_est_les")
    msgs.append("s009__est_ce_que_tu_peux_m_expliquer_la_difference_qu_il_y_a_entre_toi_et")
    msgs.append("s010__est_ce_que_tu_t_ennuies_toi")
    msgs.append("s011__tu_fais_des_trucs_particuliers")
    msgs.append("s021__j_ai_remarque_depuis_quelques_temps_que_vous_les_humains_vous_mettez_les_trucs_bleus_sur_votre_fille")
    msgs.append("s022__je_m_appelle_comment")
    msgs.append("s023__a_partir_de_certains_de_mes_propos")
    msgs.append("s024__est_ce_que_ca_vous_gene_pas_aussi_pour_vous_comprends")
    msgs.append("s025__il_y_a_marque_quelque_chose_bleu_vous_n_aviez_plus_la_meme_facon_de_respirer")
    msgs.append("s026__ca_ne_vous_pose_pas_un_probleme")
    msgs.append("s028__que_debut_quand_il_y_avait_l_autre_humain_vous_en_aviez_tous_les_deux_et_la_tu_l_as_en")
    msgs.append("s029__ca_me_concerne_pas_alors_le_truc")
    msgs.append("s030__et_toi_tu_trouve_ca_agreable_a_porter")
    #~ msgs.append("s031__")
    msgs.append("s032__ca_ne_te_gene_pas_quand_tu_racontes_des_nouvelles_personnes_pour_mieux_les_cones")
    return msgs

def demo():
    strTalkPath,mem = init()
        
    rT = 0
    rBeginT = time.time()
    rTimeLastSpeak = time.time()-10
    bForceSpeak = False
    nIdxTxt = 0
    
    msgs = loadDialogs()
    while 1:
        rT = time.time() - rBeginT
        
        breather.update()
        
        time.sleep(0.05)
        
        if 1:
            #if int(rT)%15 == 0 and time.time()-rTimeLastSpeak>2.:
            if ( random.random()>1.997 or bForceSpeak ) and not breather.isSpeaking():
                bForceSpeak = False
                if 0:
                    #~ msgs = ["oui", "d'accord", "Ah oui, je suis tout a fait d'accord!"]
                    msgs = ["moi aimer toi pas du tout tres beaucoup!","moi","pas toi"]
                    breather.sayTts(msgs[random.randint(0,len(msgs)-1)])
                else:
                    #~ nIdxTxt = random.randint(0,len(msgs)-1)
                    breather.sayFile(strTalkPath + msgs[nIdxTxt] + ".wav")
                    nIdxTxt += 1
                    if nIdxTxt >= len(msgs):
                        nIdxTxt = 0 
                rTimeLastSpeak = time.time()
            
        
        # interaction with the world
        if os.name == "nt":
            bTouch = misctools.getKeystrokeNotBlocking() != 0
            rInc = 0.05
        else:
            bTouch = mem.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value") != 0
            rInc = 0.05
            
        #~ bTouch |= misctools.getActionRequired() != False
        bForceSpeak = misctools.getActionRequired() != False
        
        if bTouch:
            breather.increaseExcitation(rInc)
            
        bExit = misctools.isExitRequired()
        
        if bExit:
            print( "Exiting..." )
            break
    # while - end
# demo - end


#~ pb: trop en arriere: -2 sur KneePitch, -4 sur ravir
#~ son sur ravir moteur: robot a 60 pour excitation a 1, 65 pour 0.5, = 90 sur mon ordi
# change now, regler pour 72 pour l'experimentation: volume correct pour la voix

def expe():
    print("INF: mode experimentation ravir  - start!!!\n")
    
    strTalkPath,mem = init()
        
    rT = 0
    rBeginT = time.time()
    rTimeLastSpeak = time.time()-10
    bForceSpeak = False
    nIdxTxt = 0
    
    msgs = loadDialogs()
    
    listHeadOrientation = [
        [0,-0.087], # face
        [0.45,0.36], # chaussure
        [0.92,-0.02], # deuxieme fenetre
        [-0.67,0.50], # placard a droite
        [1.26,0.004], # porte
    ]
    ratioTimeFirst = 0.7 # first orientation is predominant, other orientation randomly
    breather.setHeadIdleLook(listHeadOrientation,ratioTimeFirst)
    
    breather.setPaused(True)
    
    nStep = 10
    
    nDialog = 0 # diff de 0 if in a dialog, 
    
    while 1:
        rT = time.time() - rBeginT
        
        breather.update()
        
        time.sleep(0.05)
        
        if nDialog != 0:
            if not breather.isSpeaking():
                breather.sayFile(strTalkPath + msgs[nIdxTxt] + ".wav")
                nIdxTxt += 1
                if nDialog == 1 and nIdxTxt == 7:
                    nDialog = 0
                if nDialog == 2 and nIdxTxt >= len(msgs):
                    nDialog = 0
                rTimeLastSpeak = time.time()
            
        
        # interaction with the world
        if os.name == "nt":
            bTouch = misctools.getKeystrokeNotBlocking() != 0
            rInc = 0.05
        else:
            bTouch = mem.getData("Device/SubDeviceList/Head/Touch/Front/Sensor/Value") != 0
            rInc = 0.05
            
        #~ bForceSpeak = misctools.getActionRequired() != False
        strActionRequired = misctools.getActionRequired()
        #~ print(strActionRequired)
        if strActionRequired != False:
            bIsActionTouchSimulated = "touch" in strActionRequired.lower() 
            if bIsActionTouchSimulated:
                bTouch = True
                strActionRequired = False # we erase it as in real robot, we won't received it in that case
                
        if bTouch and nStep in [10,90]:
            strActionRequired = True
            
        if strActionRequired != False:
                descState = {
 10: "debut: immobile (pause)",
 20: "on enleve le paravent et on a appuyer sur sa tete, il se met en idle (respi ou perlin)",
 30: "    inclus tete alterne entre tete sujet et autres points",
 40: "lancer le dialogue, qui automatiquement déroule les phrases et enchaine (bloquer la tete pendant le dialogue) TODO",
 50: "    TODO: rallonger le dialogue => actuellement 25 et on aimerait 45. ca devrait etre avant la fin des questions quand la lumiere, le soir, les sons se font plus rare, et alors j'ai remarqué qu'il y avait plus personne et apres 22h, ... on enchaine la suite./ tourner autour du pot au début.",
 60: "ecoute active pendant x minutes, le gars parle.",
 70: "le gars a arreter de parler; repasse en idle.",
 80: "",
 90: "head pour passer en rest",
100: "    le deplace",
110: "head pour repasser en wake et mode idle",
120: "dialog 2, longueur ok, mais changer: le chercheur qui rentre et qui sort, l'a tout le temps et toi des fois tu le met et des fois tu l'enleve.",
130: "ecoute active pendant x minutes, le gars parle.",
140: "le gars arrete de parler, repasse en idle",
150: "",
160: "tape tete pour rest",
170: "remise du paravent - pret a recommencer",
                                }
                    
                # Next Action
                nStep += 10
                print("\nINF: new step: %d: %s\n" % (nStep,descState[nStep]) )
                if nStep == 20:
                    breather.setPaused(not breather.isPaused())
                    nStep += 10
                    
                if nStep == 40:
                    nDialog = 1
                    nIdxTxt = 0
                    nStep += 10
                    
                if nStep == 60:
                    breather.setListening(True)

                if nStep == 70:
                    breather.setListening(False)    
                    nStep += 10                    
            
                if nStep == 90:
                    breather.setPaused(not breather.isPaused())
                    nStep += 10
                    
                if nStep == 110:
                    breather.setPaused(not breather.isPaused())
                    
                if nStep == 120:
                    nDialog = 2
                    nIdxTxt = 7

                if nStep == 130:
                    breather.setListening(True)

                if nStep == 140:
                    breather.setListening(False)
                    nStep += 10
                    
                if nStep == 160:
                    breather.setPaused(not breather.isPaused())
                    
                if nStep == 170:
                    nStep = 10
                    
        bExit = misctools.isExitRequired()
        
        if bExit:
            print( "Exiting..." )
            break
    # while - end
# expe - end

"""
# des fois, faire un soupir, pour vider les poumons:

Dans les bronches une gaine de muscle lisse. A un moment donne ca se bloque avec de l'atp, ca devient rigide.

Une facon de remettre a l'etat souple c'est de tirer un grand coup dessus => soupir: 2 a 3 fois le soupir courant. 

Pas forcement plus longtemps. dans ce soupir qui sera plus fort, ca devrait pas etre plus fort que l'etat actuel 

(tout est moins fort donc).


# avant de parler: inspi plus vite plus fort et entendable

# retour du 2 fevrier:
- ajout du hipyawrandom (boite choregraphe) en parallele.
- ajouter tete sur parole (mot) et main et coude. (comme porteuse de sac a main) 
   avec une main predominante.
+ anim de soulagement.
   
Catherine: thesarde sur mesure de la qualite d'interaction (synchro...)

Questionnaire sur la presence fait bcp sur la RV mais pas trop avec les robots.
Comment pourrait on mesurer la presence. Vous vous sentez moins seul ?

Idee Thomas avec NAO: il pense que ca n'a pas de sens d'avoir un robot debout, c'est trop impacter.
alors qu'avec NAO qui serait assis on comprendrait qu'il est juste a cote
=> designer une chaise haute et le laisser dans la piece pour faire une presence
et il fait juste le bebe (pas besoin de parler).

Catherine croyait que c'etait une voix de synthese.
"""

"""


bandana bleu et vert + ramener une tablette pour joli et test

"""

if __name__ == "__main__":
     #~ demo()
     expe()
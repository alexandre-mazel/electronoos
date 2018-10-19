# -*- coding: utf-8 -*-
import sys
sys.path.append( "C:/Users/amazel/dev/git/protolab_group/abcdk/sdk" )

import abcdk.sound
import math
import numpy as np
import os
import struct
import time

class Boum:
    def __init__( self, rFreq, nMax = 0x7FFF, rOffset = 0. ):
        self.rFreq = rFreq
        self.rStartT = None  # will be set at first demand
        self.rOffset = rOffset
        self.nMax = nMax
        self.bIsFinished = False
        
    def getValue( self, rT ):
        if self.rStartT == None:
            self.rStartT = rT
        rCurT = (rT-self.rStartT-self.rOffset)
        if rCurT < 0.:
            return 0.
        rVal = self.nMax*math.sin(rCurT*2*math.pi*self.rFreq)
        self.nMax -= 0.1
        if self.nMax < 3: 
            self.bIsFinished = True
        return rVal
        
    def isFinished(self):
        return self.bIsFinished

def generateSong( strFilenameDest ):
    aBoum = []
    rSoundDuration = 74
    rFrequency = 40
   ##### TODO: rewrite with np !!!
    timeBegin = time.time()
    w = abcdk.sound.Wav()
    w.new()
    #~ w.addData( [0,30000, -30000] )
    rT = 0.
    nSampling = 44100
    nMax = 0x7FFF/12 # for an average of 8 sounds
    rBaseFrequencyCounter = -nMax
    rResonanceFrequencyCounter = -nMax
    rSlightDelta = 50 # 50 is like in the wikipedia
    dataBuf = []
    strFormat = "h"
    nPrintedRT = 0
    while( rT < rSoundDuration ):
        
        #~ nVal = nMax * math.sin( rT*2*math.pi*rFrequency ) # simple sinus
        
        if( 0 ):
            # Simulating a resonant filter, as seen in http://en.wikipedia.org/wiki/Phase_distortion_synthesis
            
            rBaseFrequencyCounter += rFrequency*nMax/nSampling
            if( rBaseFrequencyCounter > nMax ):
                rBaseFrequencyCounter = -nMax
                rResonanceFrequencyCounter = -nMax # resetted by base

            rResonanceFrequencyCounter += (rFrequency+rSlightDelta)*nMax/nSampling
            if( rResonanceFrequencyCounter > nMax ):
                rResonanceFrequencyCounter = -nMax
            
            #~ nVal = rBaseFrequencyCounter            
            #~ nVal = rResonanceFrequencyCounter
            #~ nVal =  nMax * math.sin( rResonanceFrequencyCounter*2*math.pi/nMax )
            nVal =  nMax * math.sin( rResonanceFrequencyCounter*2*math.pi/nMax ) * (-rBaseFrequencyCounter/nMax)
            
        if( 0 ):
            # a variation about a square signal from the sinus formulae:
            # x(t) = (pi/4) * sum[0,+inf][ ( sin((2k+1)2*pi*f*t) / (2k+1) ]
            #~ nDegrees = int( 6 * math.sin( rT / 10. ) ) + 1
            nDegrees = 6
            rVal = 0.            
            for k in range( nDegrees ):
                rVal += math.sin((2*k+1)*2*math.pi*rFrequency*rT) / (2*k+1)
            nVal = int( rVal * (nMax * math.pi/4) )
        
        if( 0 ):
            nVal = nMax * math.sin( rT*2*math.pi*rFrequency )
            nVal += nMax * math.sin( rT*2*math.pi*(rFrequency+0.5))
            
        if( 1 ):
            # a sum of sinus
            rVal = 0.
            nNbrSinus = 2
            for k in range( nNbrSinus ):
                rVal += math.sin(rT*2*math.pi*(rFrequency+(10.8*math.sin(k*0.5*rT)) ))
            nVal = int( rVal * nMax/nNbrSinus )

        # hard clipping
        if( nVal > nMax ):
            nVal = nMax
        if( nVal < -nMax ):
            nVal = -nMax
        # add boum
        #~ nVal = 0 #remove all but boum
        i = 0
        while i < len(aBoum):
            nVal = int(nVal *1. + aBoum[i].getValue( rT )*1.)
            if aBoum[i].isFinished():
                del aBoum[i]
            else:
                i += 1
            
        rT += 1./nSampling
        # w.addData( [nVal] ) # not optimal
        
        # fade in & fade out
        
        rTimeFadeIn = 2.
        if rT < rTimeFadeIn:
            nVal *= rT/rTimeFadeIn
            
        rTimeFadeOut = 6. 
        if rT > rSoundDuration - rTimeFadeOut:
            nVal *= 1 - ( (rT-(rSoundDuration - rTimeFadeOut))/rTimeFadeOut )

        # hard clipping (l'effet est sympa) (mais on perd des basses saturés)
        if 0:
            if( nVal > nMax ):
                nVal = nMax
            if( nVal < -nMax ):
                nVal = -nMax
            
        #dataBuf += struct.pack( strFormat, nVal )

        dataBuf.append(int(nVal))
        
        # print advancing & more
        nCurT = int(rT)
        if nPrintedRT != nCurT:
            print( "current: %s (aBoum:%s)" % (nCurT,len(aBoum) ) )
            nPrintedRT = nCurT
    
            if (nCurT%2) == 0:
                nVol = nMax*6
                if (nCurT%4) == 0:
                    nVol *= 0.7
                aBoum.append(Boum(40,nVol))
                # petit delai en plus
                aBoum.append(Boum(40,nVol*0.5, rOffset=0.23))
                
            #ajout un gros son disto
            if 0:
                #if nCurT >= 8 and (nCurT % 8)== 1:
                if nCurT == 32 or nCurT == 48 or nCurT == 64:
                    aBoum.append(Boum(40,nMax*10))
                    
            # petite montée de piano
            if 1:
                if nCurT >= 32 and nCurT <= 64 and (nCurT%4)==2:
                    aBoum.append(Boum(nCurT*10,nMax*0.3))
            
            # petit tic
            if nCurT >= 32 and nCurT < 76:
                for i in range(2):
                    dataBuf[-i] = 0
            
            #rFrequency +=(nCurT%4)*6
        #rFrequency+=(45-nCurT) / 1000. #nice aigu
        #rFrequency+=(45-nCurT) / 1000000.
        rFrequency= 100-abs(rT-45)/2
        
        if rT > 40 and 0:
            break
        
    # while - end
    w.data = np.array(dataBuf, dtype=np.int16)
    w.updateHeaderSizeFromDataLength()
    
    w.write( strFilenameDest )
    rDuration = time.time()-timeBegin
    print( "INF: sound.generateFatBass: generating a sound of %5.3fs in %5.3fs (%5.2fx RT)" % (rSoundDuration,rDuration,rSoundDuration/rDuration) )

    
# idee: faire un son comme un cylindre ou chaque pixel est une rondeur de son (ou un sinus)
# puis balancer des images dans ce cylindre (qui vont eteindre certains sinus)
# ou des visages
# ou des animaux
#ou des points caracteristiques d'image/de visages...
strFilename  = "c:/tmp2/generated.wav"
generateSong(strFilename)
os.system( '"C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"' + " " + strFilename )

"""
J'aime a naviguer sur les mers du savoir
et croire en le bien fondé de la chose.
Important est le sens du fleuve qui
décrit a son tour le reve de l'ame.
Ainsi l'humain aurait été un tout
sans son unicité virtuelle imbriqué dans sa tete ?
Mais en quoi le situer la, au lieu de n'importe ou ailleurs ?
En son centre, en son organe sexué ? 
en ses pieds racine et lien terrestre ?
Et pourquoi le dieu ne serait en chacun de nous
cette chose qui différencie la vie de l'objet ?
Dans le livre ceci est donné, tel qu'il apparaitrait.
Car donc toi le connaisseur, aide les autres.
Apportes leur tes savoirs et doutes.
Mais jamais ne renchérit.
"""
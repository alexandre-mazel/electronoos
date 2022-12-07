# -*- coding: cp1252 -*-

"""
analyse sound on the fly
"""

import numpy as np
import os
import time

import sound_processing
import misctools
import wav
import freespeech

class SoundAnalyser:
    def __init__( self ):
        
        # default configuration:
        self.rEnergyThreshold = 30;
        self.rWaitSilenceBeforeEnding = 0.35
        self.rLengthInterestingSound = 0.4
        self.rMaxDurationPerSend = 30.; # in second
        self.bSendToSpeechReco = True     
        self.bSpeechRecoUseSphinx = 0 # google
        #~ self.bSpeechRecoUseSphinx = 1 # sphinx
        
        print("INF: SoundAnalyser: bSpeechRecoUseSphinx: %s" % self.bSpeechRecoUseSphinx )
        
        
        self.strCurrentFilename = None;

        #~ self.rSegmentDurationForANewIncompleteCall = 0.5; # the length of each diff for a new send in second: default: 1, put a big number and you'll save some cpu but lose reactivity in long/noisy ambiance
        self.rTimeDurationLastSend = 0.;  # the time (expressed in duration) of the last send
        
        #~ self.strRobotName = mem.getData( "HAL/Robot/Type" );
        #~ if( "nao" in self.strRobotName.lower() ):
            #~ self.rEnergyThreshold = 200;
            
        self.aStoredSoundData = np.array( [], dtype=np.int16 ); # a numpy int16 array storing current sound
        self.bStoring = False; # are we currently storing ?
        self.timeLastEnergy = time.time() - 100
        
        self.wordsHeardCallback = None
        
        #~ self.strDstPath = "/tmp/";
        if os.name == "nt":
            self.strDstPath = "c:/recorded_sound/"
        else:
            self.strDstPath = os.path.expanduser("~/recorded_sound/")
        
        try:
            os.makedirs( self.strDstPath );
        except: pass
        
    
    def processBuffer( self, buffer, nSampleRate, nbrBytesPerSample, nbOfChannels, timeStamp ):
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module
        """
        bVerbose=0
        
        ts = "%.2f" % timeStamp
        aSoundData = np.fromstring( buffer, dtype = np.int16 )
        nEnergy = sound_processing.computeEnergyBestNumpy(aSoundData)
        if nEnergy > 20:
            if bVerbose: print( "%s: INF: processBuffer: energy: %s" % (ts,nEnergy) )
        
        bSendFile = False;
        bEndOfSound = False;
        if( nEnergy > self.rEnergyThreshold ):
            if bVerbose: print( "%s: DBG: processBuffer: High energy: %s" % (ts,nEnergy) )
            self.timeLastEnergy = time.time();
            self.bStoring = True;
        else:
            if( self.bStoring and time.time() - self.timeLastEnergy > self.rWaitSilenceBeforeEnding ):
                # end of the sound
                bEndOfSound = True
                
                
        if( self.bStoring ):
            if bVerbose: print( "%s: INF: processBuffer: bStoring: %s" % (ts,self.bStoring) )
            self.aStoredSoundData = np.concatenate( (self.aStoredSoundData, aSoundData) )
            #~ rSampleDuration = float(nbrOfSamplesByChannel) / self.nSampleRate;
            rCurrentDuration = len(self.aStoredSoundData) / (nSampleRate*nbOfChannels);
            if( rCurrentDuration > self.rMaxDurationPerSend and 0):
                # remove 1 sec from beginning #todo: remove the real length #todo: store all but send only the end.
                rTimeToRemove = 1.;
                self.aStoredSoundData = self.aStoredSoundData[int(nSampleRate*nbOfChannels*rTimeToRemove):]
                rCurrentDuration -= rTimeToRemove;
                # self.rTimeDurationLastSend -= rTimeToRemove; # why !?
            # TODO: check that condition !!!
            #~ if( rCurrentDuration > self.rTimeDurationLastSend + self.rSegmentDurationForANewIncompleteCall or (bEndOfSound and self.rTimeDurationLastSend == 0. ) ):
            if bEndOfSound and rCurrentDuration < self.rMaxDurationPerSend :
                bSendFile = True;
            
            
        if( bSendFile ):
            if bVerbose: print( "%s: INF: processBuffer: sending file ! (bSendFile: %s, bEndOfSound:%s)" % (ts,bSendFile,bEndOfSound) );
            if rCurrentDuration < self.rWaitSilenceBeforeEnding+self.rLengthInterestingSound:
                if bVerbose: print( "%s: INF: processBuffer: file is too short: duration: %.3fs" % (ts,rCurrentDuration) )
            else:
                self.rTimeDurationLastSend = rCurrentDuration;
                strOpionnalId = ""
                #~ strOpionnalId = "_" + self.strRobotName
                strFilename = self.strDstPath + misctools.getFilenameFromTime() + strOpionnalId + ".wav";
                self.strCurrentFilename = strFilename;
                print( "%s: INF: outputting %.3fs to a new file: %s" % (ts,rCurrentDuration,strFilename) );
                wavTemp = wav.Wav();
                wavTemp.new( nSamplingRate = nSampleRate, nNbrChannel = nbOfChannels, nNbrBitsPerSample = nbrBytesPerSample*8 );
                wavTemp.addData( self.aStoredSoundData );
                wavTemp.write( strFilename );
                
                if self.bSendToSpeechReco:
                    reco = freespeech.recognizeFromFile(strFilename, "fr-FR", self.bSpeechRecoUseSphinx)
                    if reco != None:
                        print( "%s: INF: recognized: %s" % (ts,reco) );
                        txt = reco[0]
                        conf = reco[1]
                        txtclean = txt.replace(" ", "_")
                        txtclean = txtclean[:100]
                        strFilenameNew = strFilename.replace(".wav", "__"+str(int(self.bSpeechRecoUseSphinx))+"__"+txtclean+".wav")
                        os.rename(strFilename,strFilenameNew)
                        if self.wordsHeardCallback: self.wordsHeardCallback(txt,conf)

        if( bEndOfSound ):
            if bVerbose: print( "%s: INF: processBuffer: bEndOfSound: new buffer" %(ts));
            self.aStoredSoundData = np.array( [], dtype=np.int16 );
            self.bStoring = False;
            self.rTimeDurationLastSend = 0;
                
    # processRemote - end
    
    def setWordsHeardCallback( self, callback ):
        """
        set a callback to call when words are heard
        - callback: a function with parameters: (words, confidence)
        """
        self.wordsHeardCallback = callback
        
        
        
        
# SoundAnalyser - end

soundAnalyser = SoundAnalyser()
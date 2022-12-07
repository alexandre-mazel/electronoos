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

class SoundAnalyser:
    def __init__( self ):
        
        # default configuration:
        self.rEnergyThreshold = 30;
        self.rWaitSilenceBeforeEnding = 0.35
        self.rLengthInterestingSound = 0.4
        self.rMaxDurationPerSend = 20.; # in second
        self.bSendToSpeechReco = True     
        self.bSpeechRecoUseSphinx = 1 # else it's google
        
        self.strCurrentFilename = None;

        #~ self.rSegmentDurationForANewIncompleteCall = 0.5; # the length of each diff for a new send in second: default: 1, put a big number and you'll save some cpu but lose reactivity in long/noisy ambiance
        self.rTimeDurationLastSend = 0.;  # the time (expressed in duration) of the last send
        
        #~ self.strRobotName = mem.getData( "HAL/Robot/Type" );
        #~ if( "nao" in self.strRobotName.lower() ):
            #~ self.rEnergyThreshold = 200;
            
        self.aStoredSoundData = np.array( [], dtype=np.int16 ); # a numpy int16 array storing current sound
        self.bStoring = False; # are we currently storing ?
        self.timeLastEnergy = time.time() - 100
        
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
        ts = "%.2f" % timeStamp
        aSoundData = np.fromstring( buffer, dtype = np.int16 )
        nEnergy = sound_processing.computeEnergyBestNumpy(aSoundData)
        if nEnergy > 20:
            print( "%s: INF: processBuffer: energy: %s" % (ts,nEnergy) )
        
        bSendFile = False;
        bEndOfSound = False;
        if( nEnergy > self.rEnergyThreshold ):
            print( "%s: DBG: processBuffer: High energy: %s" % (ts,nEnergy) )
            self.timeLastEnergy = time.time();
            self.bStoring = True;
        else:
            if( self.bStoring and time.time() - self.timeLastEnergy > self.rWaitSilenceBeforeEnding ):
                # end of the sound
                bEndOfSound = True
                
                
        if( self.bStoring ):
            print( "%s: INF: processBuffer: bStoring: %s" % (ts,self.bStoring) )
            self.aStoredSoundData = np.concatenate( (self.aStoredSoundData, aSoundData) )
            #~ rSampleDuration = float(nbrOfSamplesByChannel) / self.nSampleRate;
            rCurrentDuration = len(self.aStoredSoundData) / (nSampleRate*nbOfChannels);
            if( rCurrentDuration > self.rMaxDurationPerSend ):
                # remove 1 sec from beginning #todo: remove the real length
                rTimeToRemove = 1.;
                self.aStoredSoundData = self.aStoredSoundData[int(nSampleRate*nbOfChannels*rTimeToRemove):]
                rCurrentDuration -= rTimeToRemove;
                self.rTimeDurationLastSend -= rTimeToRemove;
            # TODO: check that condition !!!
            #~ if( rCurrentDuration > self.rTimeDurationLastSend + self.rSegmentDurationForANewIncompleteCall or (bEndOfSound and self.rTimeDurationLastSend == 0. ) ):
            if bEndOfSound:
                bSendFile = True;
            
            
        if( bSendFile ):
            print( "%s: INF: processBuffer: sending file ! (bSendFile: %s, bEndOfSound:%s)" % (ts,bSendFile,bEndOfSound) );
            if rCurrentDuration < self.rWaitSilenceBeforeEnding+self.rLengthInterestingSound:
                print( "%s: INF: processBuffer: file is too short: duration: %.3fs" % (ts,rCurrentDuration) )
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
                    if self.bSpeechRecoUseSphinx:
                    

        if( bEndOfSound ):
            print( "%s: INF: processBuffer: bEndOfSound: new buffer" %(ts));
            self.aStoredSoundData = np.array( [], dtype=np.int16 );
            self.bStoring = False;
            self.rTimeDurationLastSend = 0;
                
    # processRemote - end
        
        
        
        
# SoundAnalyser - end

soundAnalyser = SoundAnalyser()
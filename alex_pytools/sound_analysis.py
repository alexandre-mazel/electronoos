# -*- coding: cp1252 -*-

"""
analyse sound on the fly
"""

import numpy as np
import time

import sound_processing
import misctools
import wav

class SoundAnalyser:
    def __init__( self ):
        self.strCurrentFilename = None;
        self.rMaxDurationPerSend = 20.; # in second
        self.rSegmentDurationForANewIncompleteCall = 0.5; # the length of each diff for a new send in second: default: 1, put a big number and you'll save some cpu but lose reactivity in long/noisy ambiance
        self.rTimeDurationLastSend = 0.;  # the time (expressed in duration) of the last send
        
        self.rEnergyThreshold = 60;
        
        #~ self.strRobotName = mem.getData( "HAL/Robot/Type" );
        #~ if( "nao" in self.strRobotName.lower() ):
            #~ self.rEnergyThreshold = 200;
            
        self.aStoredSoundData = np.array( [], dtype=np.int16 ); # a numpy int16 array storing current sound
        self.bStoring = False; # are we currently storing ?
        self.timeLastEnergy = time.time() - 100
        
        self.strDstPath = "/tmp/";
        try:
            os.makedirs( self.strDstPath );
        except: pass
        
    
    def processBuffer( self, buffer, nSampleRate, nbrBytesPerSample, nbOfChannels, timeStamp ):
        """
        This is THE method that receives all the sound buffers from the "ALAudioDevice" module
        """
        
        aSoundData = np.fromstring( buffer, dtype = np.int16 )
        nEnergy = sound_processing.computeEnergyBestNumpy(aSoundData)
        if nEnergy > 20:
            print( "INF: processBuffer: nEnergy: %s" % nEnergy )
        
        bSendFile = False;
        bEndOfSound = False;
        if( nEnergy > self.rEnergyThreshold ):
            print( "DBG: High nEnergy: %s" % nEnergy )
            self.timeLastEnergy = time.time();
            self.bStoring = True;
        else:
            if( self.bStoring and time.time() - self.timeLastEnergy > 0.2 ):
                # end of the sound
                bEndOfSound = True
                
                
        if( self.bStoring ):
            print( "INF: processBuffer: bStoring: %s" % self.bStoring )
            self.aStoredSoundData = np.concatenate( (self.aStoredSoundData, aSoundData) )
            #~ rSampleDuration = float(nbrOfSamplesByChannel) / self.nSampleRate;
            rCurrentDuration = len(self.aStoredSoundData) / (nSampleRate*nbOfChannels);
            if( rCurrentDuration > self.rMaxDurationPerSend ):
                # remove 1 sec from beginning
                rTimeToRemove = 1.;
                self.aStoredSoundData = self.aStoredSoundData[int(nSampleRate*rTimeToRemove):]; # ASSUME MONO CHANNEL !
                rCurrentDuration -= rTimeToRemove;
                self.rTimeDurationLastSend -= rTimeToRemove;
            # TODO: check that condition !!!
            if( rCurrentDuration > self.rTimeDurationLastSend + self.rSegmentDurationForANewIncompleteCall or (bEndOfSound and self.rTimeDurationLastSend == 0. ) ):
                bSendFile = True;
            
            
        if( bSendFile ):
            print( "INF: processBuffer: bSendFile: %s" % bSendFile );
            self.rTimeDurationLastSend = rCurrentDuration;
            strOpionnalId = ""
            #~ strOpionnalId = "_" + self.strRobotName
            strFilename = self.strDstPath + misctools.getFilenameFromTime() + strOpionnalId + ".wav";
            self.strCurrentFilename = strFilename;
            print( "INF: outputting to a new file: %s" % strFilename );
            wavTemp = wav.Wav();
            wavTemp.new( nSamplingRate = nSampleRate, nNbrChannel = self.nNbrChannels, nNbrBitsPerSample = 16 );
            wavTemp.addData( self.aStoredSoundData );
            wavTemp.write( strFilename );

            print( "INF: processBuffer: bEndOfSound: %s" % bEndOfSound );

        if( bEndOfSound ):
            print( "INF: processBuffer: bEndOfSound: new buffer" );
            self.aStoredSoundData = np.array( [], dtype=np.int16 );
            self.bStoring = False;
            self.rTimeDurationLastSend = 0;
                
    # processRemote - end
        
        
        
        
# SoundAnalyser - end

soundAnalyser = SoundAnalyser()
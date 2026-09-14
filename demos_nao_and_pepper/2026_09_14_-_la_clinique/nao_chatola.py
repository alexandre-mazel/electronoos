"""
Pour copier sans repeter le mot de passe:

scp -o HostkeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -i "C:\Users\alexa\perso\docs\cle_ssh_pour_copier_rapidement_sur_nao_avec_scp" *.py nao@192.168.0.68:/home/nao/dev/git/electronoos/demos_nao_and_pepper/2026_09_14_-_la_clinique/

(le fichier cle_ssh_pour_copier_rapidement_sur_nao_avec_scp a ete cree avec puttygen Conversions > Export OpenSSH key et j'ai copie sur nao ma cle publique (public key for pasting...) dans ~/.ssh/authorized_keys sur une ligne)

# il faut copier ce dossier, ainsi que le sound_analyser_modified
scp -o HostkeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -i "C:\Users\alexa\perso\docs\cle_ssh_pour_copier_rapidement_sur_nao_avec_scp" c:\Users\alexa\dev\git\abcdk\sdk\abcdk\sound_analyser.py nao@192.168.0.68:/home/nao/.local/lib/python2.7/site-packages/abcdk/

"""

import sys
import time

#~ sys.path.append( "/home/nao/dev/git/electronoos/chatola")
#~ import sound_acquiring # non en fait, je ai copie le bout de code dans sound_analyser

import abcdk.sound_analyser # on copie celui de notre ordi

def sendToSpeechRecoCustom( self, strFilename ):
        """
        Send a file to the speech recognition engine.
        Return: the string of recognized text, + confidence or None if nothing recognized
        """
        print( "INF: sendToSpeechRecoCustom( %s ): starting..." % strFilename )
        return
        
        log.info("_sendToSpeechReco: sending to speech reco '%s'" % strFilename )
        retVal = None
        
        timeBegin = time.time()
        
        retVal = sound.freespeech.freeSpeech.analyse( strFilename, strUseLang=self.strUseLang )
        
        if self.bVerbose: log.info( "SoundAnalyser._sendToSpeechReco: freeSpeech: retVal: %s" % str(retVal) )
                
        rProcessDuration = time.time() - timeBegin
        
        if self.bVerbose: log.info( "SoundAnalyser._sendToSpeechReco: freeSpeech analysis processing takes: %5.2fs" % rProcessDuration )
        
        if( 0 ): # disabled
            self.rSkipBufferTime = rProcessDuration  # if we're here, it's already to zero
        
        if retVal != None:
            retVal = [ retVal[0][0], retVal[0][1] ]
            txtForRenameFile = retVal[0]
            print("recognised: %s" % str(retval))
        else:
            txtForRenameFile = "Not_Recognized"
            
        if self.bKeepAudioFiles:
            newfilename = strFilename.replace( ".wav", "__%s.wav" % stringtools.convertForFilename(txtForRenameFile) )
            baseFilename = os.path.basename(strFilename)
            newBaseFilename = os.path.basename(newfilename)
            
            newfilename = "~/recorded/prevWavs/"
            newfilename = os.path.expanduser(newfilename)
            try: os.makedirs(newfilename)
            except: pass
            newfilename += newBaseFilename
            shutil.move(  strFilename, newfilename )
            print( "INF: SoundAnalyser._sendToSpeechReco: saved wav file in " + newfilename)
        
        return retVal

abcdk.sound_analyser.SoundAnalyzer._sendToSpeechReco = sendToSpeechRecoCustom


def run_nao_chatola():
    abcdk.sound_analyser.launchSoundReceiverFromShell() # work but in another thread, so I can't patch the reco with the monkey patch du dessus
    #~ abcdk.sound_analyser.launchSoundReceiverStandalone() #  no samples received, exiting...
    while 1:
        print( "in nao chatola loop...")
        pass
        time.sleep(0.5)
        
    
    
if __name__ == "__main__":
    # syntax: scriptname <server_ip ou pas?
    run_nao_chatola()
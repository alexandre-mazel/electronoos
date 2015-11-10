# -*- coding: utf-8 -*-

#
# My Raspberry Pi Startup
# v0.7
#
# Author: A. Mazel & L. George

import datetime
import os

def executeAndGetResults(strCommand, bVerbose = False ):
    """
    get the image version without abcdk
    """
    datetimeObject = datetime.datetime.now()
    strTempOut = "/tmp/tmp_" + datetimeObject.strftime( "%Y_%m_%d-%Hh%Mm%Ss%fms" ) + ".txt";
    if( bVerbose ):
        print( "INF: executeAndGetResults: running: '%s'" % strCommand );
    os.system( "%s>%s" % (strCommand,strTempOut) );
    file = open( strTempOut, "rt" );
    strTxt = file.read();
    file.close();
    os.unlink(strTempOut);
    if( len(strTxt)> 1 and strTxt[-1]=='\n' ):
        strTxt = strTxt[:-1];
    if( bVerbose ):
        print( "INF: executeAndGetResults: results: '%s'" % strTxt );
    return strTxt;
# executeAndGetResults - end


def publishIP():
    strHostname = executeAndGetResults( "hostname" );
    strIP = executeAndGetResults( "hostname -I" );
    os.system( "wget -O /tmp/out.log 'http://perso.ovh.net/~mangedisf/mangedisque//Alma/info/inform.php?host=%s&ip=%s'" % (strHostname,strIP) );
# publishIP - end

def launch_sound_server():
    os.chdir( "/home/pi/sound_server" )
    os.system( "python sound_server.py 2>>/var/log/sound_server.log &" )
# launch_sound_server - end

publishIP();
launch_sound_server();
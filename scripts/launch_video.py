
import os
import subprocess
import time

proc = subprocess.Popen(["C:\\Program Files\\VideoLAN\\VLC\\vlc.exe","d:\\Pate_a_pizza_01__LES SECRETS DE LA PATE NAPOLITAINE _ Petrir une pate a pizza a la main _ Professeur Pizza.mp4","--no-interact", "-f", "--no-video-title-show", "--video-on-top", "--play-and-exit"])

#~ subprocess.Popen(["c:\\tmp\\VLC\\vlc.exe","d:\\Pate_a_pizza_01__LES SECRETS DE LA PATE NAPOLITAINE _ Petrir une pate a pizza a la main _ Professeur Pizza.mp4"], shell=True)
#~ subprocess.Popen('start "d:\\Pate_a_pizza_01__LES SECRETS DE LA PATE NAPOLITAINE _ Petrir une pate a pizza a la main _ Professeur Pizza.mp4"', shell=True)
#~ subprocess.Popen('"C:\Program Files\VideoLAN\VLC\vlc.exe" "d:\\Pate_a_pizza_01__LES SECRETS DE LA PATE NAPOLITAINE _ Petrir une pate a pizza a la main _ Professeur Pizza.mp4"', shell=False)
#~ os.system('"C:\Program Files\VideoLAN\VLC\vlc.exe" "d:\\Pate_a_pizza_01__LES SECRETS DE LA PATE NAPOLITAINE _ Petrir une pate a pizza a la main _ Professeur Pizza.mp4"')

while 1:
    # wait program is finished and do things...
    time.sleep(0.1)
    if proc.poll() != None:
        break
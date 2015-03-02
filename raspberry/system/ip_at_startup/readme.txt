# to have the ip at startup on a remove server
Ma methode a la main:
1. copier startup_pi.py dans le home
2. ajouter dans /etc/rc.local un ordre de lancement du script (juste avant le "exit(0)")
par exemple:
#!/bin/sh -e
#
# rc.local
...

python /home/pi/startup_pi.py

exit 0
<eof>

3. L'ip apparait ensuite sur ce site a la fin:
http://mangedisque.com/Alma/info/inform.php

4. En option, i vous voulez changer de site ou ... ci joint le php, a titre indicatif, 
car il doit falloir des libs ou ...

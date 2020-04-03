#!/bin/sh

file_bootlog="/home/pi/boot_time.txt" 
file_first="/tmp/alexscript_started"

date >> "$file_bootlog"

if [ -f "$file_first" ]
then
	exit 0
else
	echo start > "$file_first"
	echo "first time" >> "$file_bootlog"
fi

#bash -c "/usr/bin/python2.7 /home/pi/dev/git/electronoos/quick_scripts/stat_connected.py" &
/home/pi/dev/git/electronoos/quick_scripts/stat_connected.py


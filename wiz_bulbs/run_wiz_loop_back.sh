#!/bin/bash

SCRIPT="ccc_wiz_program.py"

# Boucle infinie
while true; do
    echo "Lancement de $SCRIPT..."

    python3 $SCRIPT

    # Code retour de python
    RET=$?
    echo "Le script s'est arrêté avec le code $RET. Redémarrage dans 2 secondes..."
    echo "ccc_wiz_error $RET" >>/home/pi/logs/ccc_wiz_program.log
    sleep 2
done

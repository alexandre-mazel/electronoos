#!/bin/bash

# Nom du script Python à lancer
SCRIPT="ccc_wiz_program.py"

# Boucle infinie
while true; do
    echo "Lancement de $SCRIPT..."
    
    # Exécution du script Python
    python3 $SCRIPT
    
    # Code retour de python
    RET=$?
    echo "Le script s'est arrêté avec le code $RET. Redémarrage dans 2 secondes..."
    echo "ccc_error $RET" >>/home/pi/logs/ccc_wiz_program.log
    # Petite pause (modifiable)
    sleep 2
done

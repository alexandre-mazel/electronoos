faire un lien symbolique depuis /var/www/temp.py vers le fichier ici temp.py:
sudo ln -s temp.py /var/www/html/temp.py 
(mais ca fonctionne pas (limite de droit) => faire une copy:
sudo cp temp.py /var/www/html/temp.py


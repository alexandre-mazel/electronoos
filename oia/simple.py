import os

filename = "/tmp/save_prenom.txt"

if not os.path.isfile(filename):
    firstname = input("Comment tu t'appelle?")
    file = open(filename,"w")
    file.write(firstname)
    file.close()
else:
    file = open(filename,"r")
    firstname = file.read()
    file.close()

print("Bonjour " + firstname)
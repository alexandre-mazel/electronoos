# -*- coding: cp1252 -*-
import random

input("Choisis un nombre entre 1 et 20 dans ta tête, puis appuie sur entrée quand tu es pret")
print("")

x = random.randint(1,20)
while 1:
    answer = input("Est-ce %d ?\n(écris + si c'est plus grand que %d, - si c'est plus petit ou = si c'est égal)? " % (x,x) )
    if answer == '=':
        print("Je suis trop fort!")
        break
    if answer == '+':
        x += 1
    else:
        x -= 1
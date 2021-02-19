import sys

def interact():
    f = open("/tmp/interact","at")
    f.write("1")
    f.close()

cpt = 1
while 1:
    print("appuie sur entree pour passer a la suite...")
    #~ ch = getch()
    sys.stdin.read(1)
    print(cpt)
    interact()
    cpt += 1
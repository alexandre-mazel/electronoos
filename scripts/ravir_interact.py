import sys

def interact():
    f = open("/tmp/interact","at")
    f.write("interact") # or post a number
    f.close()

def nextstep():
    f = open("/tmp/interact","at")
    f.write("next")
    f.close()
    
cpt = 1
while 1:
    print("appuie sur entree pour passer a la suite...")
    #~ ch = getch()
    ch = sys.stdin.read(1)
    print(cpt)
    nextstep()
    cpt += 1
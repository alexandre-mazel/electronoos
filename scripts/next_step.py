import sys
print( "Press enter to go to next step")
while 1:
    # filler=input() #doestn't work on pepper
    filler = sys.stdin.readline()
    print("Next...")
    f = open("/tmp/interact","wt")
    f.write("next")
    f.close()
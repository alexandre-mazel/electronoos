import os

def move_download():
    

#~ def loop_move_download():
    

ret = os.system("c:\exe\pscp -pw puba32puc c:/tmp/a.txt publac@robot-enhanced-education.org:/home/publac/")
print("ret: %s" % ret )
if ret == 0:
    print("Success !!!" )
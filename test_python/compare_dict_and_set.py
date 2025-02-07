# compare un set pour tester l'unicite d'une valeur
d = {}
s = set()
#~ for i in range(1000000):
    #~ d[i] = 1
    #~ s.add(i)
    
def add_dict(n):
    if n in d:
        return False
    d[n] = 1
    return True
    
def add_set(n):
    if n in s:
        return False
    s.add(n)
    return True
    
def check_dict(n):
    if n in d:
        return False
    return True
    
def check_set(n):
    if n in s:
        return False
    return True
    
import time
for name,func in [("add_set",add_set),("add_dict",add_dict),("check_set",check_set),("check_dict",check_dict)]:
    time_begin = time.time()
    i = 0
    while i < 20*1000*1000:
        func(i)
        i += 1
    print("time for %s: %.3fs" % (name,time.time()-time_begin))
"""
# difference not too different, but dict win (sadly)
# mstab7
time for add_set: 3.161s
time for add_dict: 3.094s
time for check_set: 2.195s
time for check_dict: 2.080s
"""
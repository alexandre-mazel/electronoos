#!/user/bin/env python
"""
Resolve the DNS/IP address of a given domain or ip

@filename resolveDNS.py
@version 1.6 (python ver 2.7.3 and python v3)
@author LoanWolffe + A. Mazel
"""
import sys
sys.path.append("../alex_pytools")
import nettools

sys.path.append("../reverse_dns")
try: import reversedns
except: pass


# test it

def getAllPossible(x):
    print("%s:"% x)
    a = nettools.getIP(x)
    b = nettools.getIPx(x)
    b2 = nettools.getIPV6x(x)
    b3 = nettools.getIPV6Sub(x)
    c = nettools.getHost(x)
    d = nettools.getAlias(x)
    
    

    try:
        import reversedns
        e = reversedns.getIP(x)
        if e != False:
            ip_to_use = e
        f = reversedns.getNames(x)
        if a != False:
            g1 = reversedns.getName(a)
            h1 = reversedns.getNames(a)
        if e != "":
            g2 = reversedns.getName(e)
            h2 = reversedns.getNames(e)
    except BaseException as err:
        print("DBG: getAllPossible: err (1): %s" % str(err))
        e = False
        f = False

    print("    IP ", a)
    print("    IPx ", b)
    print("    IPV6 ", b2)
    print("    IPV6Sub ", b3)
    print("    Host ", c)
    print("    Alias ", d)
    
    print("    rdns.getIP ", e)
    print("    rdns.getNames ", f)
    if a != False:
        print("    rdns.getName(%s): %s" %(a,g1) )
        print("    rdns.getNames(%s): %s" %(a,h1) )
    if e != "":
        print("    rdns.getName(%s): %s" %(e,g2) )
        print("    rdns.getNames(%s): %s" %(e,h2) )

def autotest():

    getAllPossible("obo-world.com")
    getAllPossible("engrenage.studio")
    getAllPossible("human-machine-interaction.org")
    getAllPossible("78.199.86.189")
    getAllPossible("192.168.158.51")
    getAllPossible("172.217.20.74")
    getAllPossible("stackoverflow.com")
    getAllPossible("youtube.com")
    getAllPossible("web.whatsapp.com")
    getAllPossible("whatsapp.com")
    getAllPossible("2a00:1450:4007:80a::200a")
    getAllPossible("2a00:1450:4007:80b::200a")
    getAllPossible("2a00:1450:4007:80d::200a")
    getAllPossible("2a02:26f0:2b00:12::5f64:5545")
    getAllPossible("fe80::20c4:b6f:84d5:565c")
    getAllPossible("2a01:e34:ec75:6bd0:f8ff:fa45:f8ae:4086")
    getAllPossible("ff02::1:3")
    getAllPossible("13.248.212.111")
    
    
"""
# current output on 2023-11-20:

obo-world.com:
    IP  '78.199.86.189'
    IPx  ['78.199.86.189']
    Host  False
    Alias  []
engrenage.studio:
    IP  '78.199.86.189'
    IPx  ['78.199.86.189']
    Host  False
    Alias  []
human-machine-interaction.org:
    IP  '78.199.86.189'
    IPx  ['78.199.86.189']
    Host  False
    Alias  []
78.199.86.189:
    IP  '78.199.86.189'
    IPx  ['78.199.86.189']
    Host  'cap33-1_migr-78-199-86-189.fbx.proxad.net'
    Alias  []
192.168.158.51:
    IP  '192.168.158.51'
    IPx  ['192.168.158.51']
    Host  'MSTAB7'
    Alias  []
172.217.20.74:
    IP  '172.217.20.74'
    IPx  ['172.217.20.74']
    Host  'sof02s49-in-f10.1e100.net'
    Alias  []
stackoverflow.com:
    IP  '104.18.32.7'
    IPx  ['104.18.32.7', '172.64.155.249']
    Host  False
    Alias  []
youtube.com:
    IP  '142.250.178.142'
    IPx  ['142.250.178.142']
    Host  'par10s49-in-x0e.1e100.net'
    Alias  []
2a00:1450:4007:80d::200a:
    IP  False
    IPx  False
    Host  'par10s21-in-x0a.1e100.net'
    Alias  False
2a02:26f0:2b00:12::5f64:5545:
    IP  False
    IPx  False
    Host  'g2a02-26f0-2b00-0012-0000-0000-5f64-5545.deploy.static.akamaitechnologies.com'
    Alias  False
"""


if __name__ == "__main__":
    if len(sys.argv)<2:
        autotest()
        exit(1)
    getAllPossible(sys.argv[1])
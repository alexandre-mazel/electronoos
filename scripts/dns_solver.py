

#!/user/bin/env python
"""
Resolve the DNS/IP address of a given domain
data returned is in the format:
(name, aliaslist, addresslist)
@filename resolveDNS.py
@version 1.01 (python ver 2.7.3)
@author LoanWolffe
"""
import socket

def getIP(d):
    """
    This method returns the first IP address string
    that responds as the given domain name
    """
    try:
        data = socket.gethostbyname(d)
        ip = repr(data)
        return ip
    except Exception:
        # fail gracefully!
        return False
#
def getIPx(d):
    """
    This method returns an array containing
    one or more IP address strings that respond
    as the given domain name
    """
    try:
        data = socket.gethostbyname_ex(d)
        ipx = repr(data[2])
        return ipx
    except Exception:
        # fail gracefully!
        return False
#
def getHost(ip):
    """
    This method returns the 'True Host' name for a
    given IP address
    """
    try:
        data = socket.gethostbyaddr(ip)
        host = repr(data[0])
        return host
    except Exception:
        # fail gracefully
        return False
#
def getAlias(d):
    """
    This method returns an array containing
    a list of aliases for the given domain
    """
    try:
        data = socket.gethostbyname_ex(d)
        alias = repr(data[1])
        #print repr(data)
        return alias
    except Exception:
        # fail gracefully
        return False
#

# test it

def getAllPossible(x):
    print("%s:"% x)
    a = getIP(x)
    b = getIPx(x)
    c = getHost(x)
    d = getAlias(x)

    print("    IP ", a)
    print("    IPx ", b)
    print("    Host ", c)
    print("    Alias ", d)    

def autotest():

    getAllPossible("obo-world.com")
    getAllPossible("engrenage.studio")
    getAllPossible("human-machine-interaction.org")
    getAllPossible("78.199.86.189")
    getAllPossible("192.168.158.51")
    getAllPossible("172.217.20.74")
    getAllPossible("stackoverflow.com")
    getAllPossible("youtube.com")
    getAllPossible("2a00:1450:4007:80d::200a")
    getAllPossible("2a02:26f0:2b00:12::5f64:5545")
    
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
    autotest()
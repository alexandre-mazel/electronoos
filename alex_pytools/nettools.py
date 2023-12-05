import os
try:
    import urllib.request # pip install requests # pas sur, pb sur python2 rpi
except BaseException as err: print("WRN: urllib.request load error. err: %s" % err)
try:
    import http.client
except BaseException as err: print("WRN: urllib.client load error. err: %s" % err)

import misctools
import socket

def getHostName():
    if os.name == "nt":
        hostname = os.environ['COMPUTERNAME']
    else:
        unames = os.uname()
        #~ print("unames: %s" % str(unames))
        hostname = unames[1]
        #~ print(hostname)
    return hostname.replace(" ", "_")


def download(remote,dst, bForceDownload=False, bInternalCalledForRetry = False):
    """
    Return a 1 if downloaded, 2 if already existing, 
    or <0 on error:
        -1: error 404: not found
        -2: error 403: forbidden
        -3: temp error
        -5: error timeout
        -50: unknown error
        -100: ValueError
        -200: invalid url
    - bInternalCalledForRetry: mechanism to try again, one time if connection  reset 
    """
    timestamp = misctools.getTimeStamp()
    if not bForceDownload and os.path.isfile(dst):
        print("%s: INF: download: file already exist: '%s'" % (timestamp,dst))
        return 2
    print("%s: INF: download: downloading '%s'" % (timestamp,remote))
    try:
        urllib.request.urlretrieve(remote, dst)
    except urllib.error.HTTPError as err:
        print("%s: ERR: common.download (1): %s\n err: %s" % (timestamp,remote,err) )
        if "404" in str(err):
            return -1
        if "403" in str(err):
            return -2
        return -50
    except ValueError as err:
        print("%s: ERR: common.download (2): %s\n err: %s" % (timestamp,remote,err) )
        return -100
    except http.client.InvalidURL as err:
        print("%s: ERR: common.download (3): %s\n err: %s" % (timestamp,remote,err) )
        return -200 
    except urllib.error.URLError as err:
        print("%s: ERR: common.download (4): %s\n err: %s" % (timestamp,remote,err) )
        if not bInternalCalledForRetry:
            return download(remote,dst,bForceDownload=bForceDownload,bInternalCalledForRetry=True)
        return -3
        
    print("%s: INF: => %s" % (timestamp,dst))
    print("%s: INF: [OK]" % timestamp)
    return 1
# download - end

def sendDataToEngServer( dataname, value, timestamp = None ):
    """
    return nbr of data sent (normally 1, but could happens than some will be sent in a burst
    
    - timestamp: if the data is from another time, you can specify it, else it will be server time
    
    """
    print("INF: sendDataToEngServer: data: %s, value: %s" % (dataname,value) )
    nbr_data_sent = 0
    try:
        
        import requests
        hostname = getHostName()
        req = "?h=%s&dn=%s&dv=%s" % (hostname,dataname,value)
        if timestamp != None:
            req += "&t=%s" % timestamp
        fullreq = "http://engrenage.studio/record_data.py" + req
        print("DBG: sendDataToEngServer: req: " + str(req) )
        requests.get(fullreq)
        print("INF: sendDataToEngServer: done")
        nbr_data_sent += 1
        
    except BaseException as err:
        print("ERR: sendDataToEngServer: err (1): %s" % err )
    
    return nbr_data_sent
    

def getLocalIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()    
    print("DBG: getLocalIP: " + IP)
    return IP
    
def getLocalIP6():
        """
        Get's local ipv6 address
        TODO: What if more than one interface present ?

        :return: IPv6 address as a string
        :rtype: string
        
        ipv6: 8 champs:
            - 3 pour le prefixe de site
            - 1 pour id de sous reseau
            - 4 pour id d'interface
        """
        try:
            s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            s.connect(('2001:4860:4860::8888', 1))
            IP = s.getsockname()[0]
        except BaseException as err:
            print("ERR: getLocalIP6: " + str(err))
            IP = '::1'
        finally:
            if 's' in locals():
                s.close()
        print("DBG: getLocalIP6: " + IP)
        return IP
        
def getIP(d):
    """
    This method returns the first IP address string
    that responds as the given domain name
    """
    try:
        data = socket.gethostbyname(d)
        ip = data
        return ip
    except socket.gaierror as err:
        pass
    return False
        
def getIPx(d):
    """
    This method returns an array containing
    one or more IP address strings that respond
    as the given domain name
    """
    try:
        data = socket.gethostbyname_ex(d)
        ipx = data[2]
        return ipx
    except socket.gaierror as err:
        pass
    return False
    

def getIPV6x(d):
    try:
        datas = socket.getaddrinfo(d, None, socket.AF_INET6)
        #~ print(datas)
        out = []
        for data in datas: 
            out.append( data[4][0])
        return out
    except socket.gaierror as err:
        pass
    return []
    
def getIPV6Sub(d):
    datas = getIPV6x(d)
    #~ if datas == False:
        #~ return datas
    out = set()
    for data in datas:
        out.add(reduceIPV6ToDomainSubPart(data))
    out = list(out)
    return out
        
def getHost(ip):
    """
    This method returns the 'True Host' name for a
    given IP address
    """
    try:
        data = socket.gethostbyaddr(ip)
        host = data[0]
        return host
    except (socket.herror,socket.gaierror) as err:
        pass
    return False

def getAlias(d):
    """
    This method returns an array containing
    a list of aliases for the given domain
    """
    try:
        data = socket.gethostbyname_ex(d)
        alias = data[1]
        #print repr(data)
        return alias
    except socket.gaierror as err:
        pass
    return False
    
    
def reduceIPV6ToDomainSubPart(ip):
    """
    2a00:1450:4007:80c::200a => 2a00:1450:4007
    """
    if not ":" in ip:
        # c'est un ip v4
        return ip
    splitted = ip.split(":")
    return ":".join(splitted[:4]) # :3, mais en fait avec :4, ca differencie mieux les services
    
def reduceDomainToMasterDomain(domain):
    """
    g2a02-26f0-2b00-0012-0000-0000-5f64-5545.deploy.static.akamaitechnologies.com => akamaitechnologies.com
    """
    splitted = domain.split(".")
    out = ".".join(splitted[-2:])
    if len(out)<6: # "co.nz"
        out = ".".join(splitted[-3:])
    return out

"""
Pourquoi 47.246.146.94 ne se resoud pas en alibaba ?

NetRange:       47.235.0.0 - 47.246.255.255
CIDR:           47.244.0.0/15, 47.240.0.0/14, 47.235.0.0/16, 47.236.0.0/14, 47.246.0.0/16
NetName:        AL-3
NetHandle:      NET-47-235-0-0-1
Parent:         NET47 (NET-47-0-0-0-0)
NetType:        Direct Allocation
OriginAS:
Organization:   Alibaba Cloud LLC (AL-3)
RegDate:        2016-04-15
Updated:        2017-04-26
Ref:            https://rdap.arin.net/registry/ip/47.235.0.0

47.246.146.94:
    IP  47.246.146.94
    IPx  ['47.246.146.94']
    IPV6  []
    IPV6Sub  []
    Host  False
    Alias  []


alibaba.com:
    IP  47.246.131.55
    IPx  ['47.246.131.55', '47.246.131.30']
    IPV6  []
    IPV6Sub  []
    Host  False
    Alias  []

aliexpress.com:
    IP  47.246.173.30
    IPx  ['47.246.173.30', '47.246.173.237']
    IPV6  []
    IPV6Sub  []
    Host  False
    Alias  []

fr.aliexpress.com:
    IP  47.246.146.94
    IPx  ['47.246.146.94']
    IPV6  []
    IPV6Sub  []
    Host  False
    Alias  ['fr.aliexpress.com', 'global.aserver-ae.aliexpress.com', 'global.aserver-ae.aliexpress.com.gds.alibabadns.com', 'eu.aserver-ae.aliexpress.com']

"""
    
def autoTest():
    #~ sendDataToEngServer("dummy", 1.23)
    print(reduceDomainToMasterDomain("maps.google.co.nz"))


if __name__ == "__main__":
        autoTest()
    
    
    
import os
import urllib.request
import http.client

import misctools

def getHostName():
    if os.name == "nt":
        hostname = os.environ['COMPUTERNAME']
    else:
        unames = os.uname()
        #~ print("unames: %s" % str(unames))
        hostname = unames[1]
        print(hostname)
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
            return download(remote,dst,bForceDownload=bForceDownload,bInternalRetry=True)
        return -3
        
    print("%s: INF: => %s" % (timestamp,dst))
    print("%s: INF: [OK]" % timestamp)
    return 1
# download - end

def sendDataToEngServer( dataname, value, timestamp = None ):
    """
    - timestamp: if the data is from another time, you can specify it, else it will be server time
    """
    print("INF: sendDataToEngServer: data: %s, value: %s" % (dataname,value) )
    import requests
    hostname = getHostName()
    req = "?h=%s&dn=%s&dv=%s" % (hostname,dataname,value)
    if timestamp != None:
        req += "&t=%s" % timestamp
    fullreq = "http://engrenage.studio/index.py" + req
    print("DBG: sendDataToEngServer: req: " + str(req) )
    requests.get(fullreq)
    print("INF: sendDataToEngServer: done")

    
def autoTest():
    sendDataToEngServer("dummy", 1.23)


if __name__ == "__main__":
        autoTest()
    
    
    
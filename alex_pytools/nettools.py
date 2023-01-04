import os
import urllib.request
import http.client

import misctools

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
    
import os
import urllib.request
import http.client

import misctools

def download(remote,dst, bForceDownload=False):
    """
    Return a 1 if downloaded, 2 if already existing, 
    or <0 on error:
        -1: error 404: not found
        -2: error 403: forbidden
        -5: error timeout
        -50: unknown error
        -100: ValueError
        -200: invalid url
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
        
    print("%s: INF: => %s" % (timestamp,dst))
    print("%s: INF: [OK]" % timestamp)
    return 1
    
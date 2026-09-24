# evite que le requests pris soit celui du dossier obo/requests! C'est moche et pas de chance!
# ca fonctionne pas car en fait c'est dans le dossier courant qu'on a un requests

#~ import sys
#~ obo_paths = []
#~ for path in sys.path[:]:
    #~ if path.endswith("/obo") or path.endswith("/obo/"):
        #~ sys.path.remove(path)
        #~ obo_paths.append(path)

#~ import requests

#~ sys.path.extend(obo_paths) # on le remet a la fin, c'est pas si pire...

# j'ai juste dupliqué la lib en un autre nom
import requestsdup as requests

import sys
import time

print(requests)
print(requests.__file__)
print(requests.__version__)

"""
La boucle principale en version audio et tts est depuis audio_analyser.py
La version web est depuis ici, appellé depuis chatola.htm (mais ca fonctionne pas depuis obor que depuis python server
"""

chatola_url = "https://obo-world.com:10000"
chatola_url = "https://engrenage.studio:45001"
chatola_url = "http://engrenage.studio:45001"

def test_data(url):
    service = url + "/data"
    response = requests.post(service, json={"msg": "hello"})
    print(response.json())
    
def ask_tchat(url, user_id, msg):
    service = url + "/tchat"
    try:
        response = requests.post(service, json={"user_id": user_id, "msg": msg}, verify=True,timeout=(10, 600)) # 10sec de timeout sur la co et 480 ou 600 sur la reponse
    except requests.exceptions.ConnectionError as err:
        ret = "ERR: ask_tchat: Impossible to connect to Chatola Server"
        return ret
    except requests.exceptions.ReadTimeout as err:
        ret = "ERR: ask_tchat: time out in Server: " + str( err )
        return ret
        
    dicres = response.json()
    if "debug" in dicres and dicres["debug"] != "":
        print( "DBG: ", dicres )
    ret = "???"
    try: 
        ret = dicres["ans"]
    except KeyError:
        pass
    return ret
    
#~ test_data()
#~ ask_tchat( "test", "hello" )

def loop_dialog( chatola_url, user_id ):
    while 1:
        msg = input( "You: " )
        if msg == "":
            continue
        if msg.lower() in ["bye", "a+", "quit", "quit()"]:
            print( "Quitting...")
            break
        time_begin = time.time()
        ans = ask_tchat( chatola_url, user_id, msg )
        print( "IA: %s" % ans )
        duration = time.time() - time_begin
        print( "    (generated in %.2fs)" % duration )
        
def index( req ):
    """
    receive ?id=toto&q=coucou
    """
    sys.path.append("../engrenage.studio")
    sys.path.append("/home/na/dev/git/electronoos/engrenage.studio/")
    import viewcloud
    print("DBG: chatola_client.py.index: req.args: '%s'" % req.args )


    dArgs = ( viewcloud.decode_param( req.args ) )
    print( "DBG: index: dArgs: %s" % str(dArgs) )
    
    user_id = dArgs["id"]
    msg = dArgs["q"]
    ask_tchat( chatola_url, user_id, msg )
    ans = ask_tchat( chatola_url, user_id, msg )
    print( "INF: chatola_client.index: IA: %s" % ans )
    
    return viewcloud.send_json({
    "success": False,
    "ans": ans
})

    
           
def test_index():
    class Req:
        pass
    req = Req()
    req.args = "id=toto&q=coucou"
    index( req )
    
if __name__ == "__main__":
    
    if 0:
        test_index()
        exit(0)


    if len(sys.argv) > 1:
        chatola_url = sys.argv[1]
    print( "INF: chatola_url: '%s'" % chatola_url )
    loop_dialog( chatola_url, "Tester")
    
    

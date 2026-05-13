import requests
import sys
import time

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
                
    
if __name__ == "__main__":
    chatola_url = "https://obo-world.com:10000"
    if len(sys.argv[1]) > 1:
        chatola_url = sys.argv[1]
    print( "INF: chatola_url: '%s'" % chatola_url )
    loop_dialog( chatola_url, "Tester")
    
    

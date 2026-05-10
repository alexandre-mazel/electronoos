import requests
import time

url = "https://obo-world.com:10000"

def test_data():
    service = url + "/data"
    response = requests.post(service, json={"msg": "hello"})
    print(response.json())
    
def ask_tchat(user_id, msg):
    service = url + "/tchat"
    try:
        response = requests.post(service, json={"user_id": user_id, "msg": msg}, verify=True)
    except requests.exceptions.ConnectionError as err:
        ret = "ERR: Impossible to connect to Chatola Serveur"
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

def loop_dialog( user_id ):
    while 1:
        msg = input( "You: " )
        if msg == "":
            continue
        if msg.lower() in ["bye", "a+", "quit", "quit()"]:
            print( "Quitting...")
            break
        time_begin = time.time()
        ans = ask_tchat( user_id, msg )
        print( "IA: %s" % ans )
        duration = time.time() - time_begin
        print( "    (generated in %.2fs)" % duration )
                
    
loop_dialog( "Tester")
    
    

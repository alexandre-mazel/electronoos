import requests

url = "https://obo-world.com:10000"

def test_data():
    service = url + "/data"
    response = requests.post(service, json={"msg": "hello"})
    print(response.json())
    
def ask_tchat(user_id, msg):
    service = url + "/tchat"
    response = requests.post(service, json={"user_id": user_id, "msg": msg}, verify=True)
    dicres = response.json()
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
        if msg.lower() in ["bye", "a+", "quit"]:
            print( "Quitting...")
            break
        ans = ask_tchat( user_id, msg )
        print( "IA: %s" % ans )
    
loop_dialog( "Tester")
    
    

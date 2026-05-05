import ollama

strModel = "llama3"

class TchatUser:    
    def __init__( self, firstname = "", name = "" ):
        """
        Name is a nicely name
        """
        self.firstname = firstname
        self.name = name
        self.context = [] # a list of sentence sent to tchatter
        
    def getAns( self, msg ):
        
        response = ollama.chat( model=strModel, messages=[  {"role": "user", "content": msg} ], options= {"temperature": 0.0, "thinking":1,"seed": 1234}  )
        print(response)
        res = response["message"]["content"]
        return res

class TchatUserManager:
    
    def __init__( self ):
        self.users = {} # user_id => TchatUser
        
    def createUser( self, user_id ):
        u = TchatUser()
        self.users[user_id] = u
        
    def getUser( self, user_id ):
        if not user_id in self.users:
            self.createUser( user_id )
        return self.users[user_id]
    

tum = TchatUserManager()

def handle_user_tchat(user_id, msg):
    u = tum.getUser( user_id )
    ans = u.getAns( msg )
    return ans
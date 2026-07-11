# -*- coding: utf-8 -*-

import knowledge

import http_chat


strModel = "gemma3:270m" # un rapide pour tester
strModel = "llama3.2"

class TchatUser:    
    def __init__( self, user_id, firstname = "", name = "" ):
        """
        Name is a nicely name
        """
        self.user_id = user_id
        self.firstname = firstname
        self.name = name
        self.context = [] # a list of sentence sent to tchatter
        self.context = [{"role":"system","content":"Tu es un chatbot sympa. Répond toujours avec des phrases pas trop longues et limitées a 2 ou phrases max en texte pur, sans émoticone ou truc fancy du genre."}]
        if 0:
            self.context.append( {"role":"system","content":"Si on te demande un restaurant dans le coin (on est dans le 16ieme arrt de paris), tu peux parler de Ragazzi 2.0 au 83 rue de Longchamp ou La matta au 23 rue de l'annonciation"} )
        
        self.prev_kdb = []
        
    def getAns( self, msg ):
        
        #~ response = ollama.chat( model=strModel, messages=[  {"role": "user", "content": msg} ], options= {"temperature": 0.0, "thinking":1,"seed": 1234}  )
        #~ print(response)
        #~ res = response["message"]["content"]
        
        print( "DBG: TchatUser.getAns: name: %s, context:\n%s" % (self.user_id,self.context) )
        
        self.context.append({"role":"user","content":msg})
        
        """
        et ensuite ce message doit fonctionner:
        hello 2 fois doit pas donner la meme reponse
        actuellement:
        Hello! How can I assist you today?
        my name is alexandre, memorize it! now what's my name ?
        """
        
        prompt = []
        
        
        if 1:
            kdb = []
            kdb = knowledge.get_knowledge_related_to( msg )
            
                # mettre aussi des infos sur paris un peu plus globale et le tourisme en france
            if "manger" in msg and 0:
                kdb = [
                    "restaurant italien La Petite Tour au 11 rue de la Tour 75116 Paris",
                    "restaurant Le Paris Seize au 18 rue des Belles Feuilles 75116 Paris",
                    "pizzeria Pop's Pizza proche de l’avenue Victor Hugo 75116 Paris",
                    "restaurant japonais Planet Sushi avenue Victor Hugo 75116 Paris",
                    "place du Trocadéro idéale pour voir la tour Eiffel"
                ]
            
            # je pense qu'il faut garder les resultats de connaissances sur au moins 3-5 echanges
            # sinon si il file une adresse de resto, et que je dit c'est ou? il a oublié entre temps
            # j'ai monté les token a 8k dans le systeme du daemon (a reloader)
            
            if 0:
                # just this one
                for k in kdb:
                    print( "Adding k: '%s'" % str(k) )
                    prompt.insert(0, {"role": "system","content": k} )
                    
            if 1:
                # memorize prev
                self.prev_kdb.append( kdb )
                if len( self.prev_kdb ) > 4:
                    del self.prev_kdb[0]
                for kdb in self.prev_kdb:
                    print( "\nOther kdb: ")
                    for k in kdb:
                        print( "Adding k: '%s'" % str(k) )
                        prompt.append( {"role": "system","content": k} )

        print( "avant doublons: prompt: %d" % len(prompt) )
        # vire les doublons
        prompt = list({
            tuple(sorted(d.items())): d 
            for d in prompt
        }.values())
        
        print( "apres doublons: prompt: %d" % len(prompt) )

        prompt.extend(self.context[:])

        res = http_chat.ask_ollama_http( strModel, prompt )
        
        if "ERR: " not in res:
            self.context.append({"role":"assistant", "content": res})
                
        return res

class TchatUserManager:
    
    def __init__( self ):
        self.users = {} # user_id => TchatUser
        
    def createUser( self, user_id ):
        u = TchatUser( user_id )
        self.users[user_id] = u
        
    def getUser( self, user_id ):
        if not user_id in self.users:
            self.createUser( user_id )
        return self.users[user_id]
    

tum = TchatUserManager()

knowledge.classic_init()

def handle_user_tchat(user_id, msg):
    u = tum.getUser( user_id )
    ans = u.getAns( msg )
    return ans
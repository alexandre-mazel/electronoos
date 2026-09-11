# -*- coding: utf-8 -*-

"""
La partie serieuse du tchat.
- Embedding pour retrieving du contexte avec qwen3-embedding (cf knowledge, ligne 15)
- Discussion avec llama3.2 (cf ce fichier ligne 15)

Perf sur Champion1 avec qwen3-embedding, parfois 2sec, c'est un peu long. (car il charge/décharge le modele entre chaque appel pour recharger llama, argh)
En passant le contexte de qwen3-embedding a 4k (ce qui est normal vu que j'envoie des phrases pas trop longues), ca rentre en ram sur la 3080 (10GB).
(c'est un peu la honte d'ailleurs d'utiliser un modele aussi gros pour l'embedding comparé a llama3.2 qiu fait un boulot important aussi!)

NAME                      ID              SIZE      PROCESSOR    CONTEXT
llama3.2:latest           a80c4f17acd5    3.4 GB    100% GPU     8192
qwen3-embedding:latest    64b933495768    6.2 GB    100% GPU     4096

On arrive a du 145ms pour l'embedding puis du 2.5s pour le tchat. c'est mieux !

Commande pour voir les chargements:
OLLAMA_HOST=127.0.0.1:11435 watch -n 1 ollama ps

En passant si ca crashe pleins de ligne dans la fenetre ollama serve, c'est souvent que ca recharge un modele en vram

On pourrait reduire l'embedding et muscler plus le chat.
Par exemple en prenant nomic-embed-text ou bge-m3? ou snowflake-arctic-embed? TODO: a tester!
Et muscler le chat avec (d'apres chatty):
Qwen3 4B - probablement mon premier choix. Meilleur en raisonnement et généralement plus solide en français/code que Llama 3.2 3B, tout en restant relativement léger.
Gemma 3 4B - très bon modèle généraliste, particulièrement agréable pour les conversations et le français.
Qwen2.5 3B - si tu veux rester très léger ; souvent une amélioration par rapport à Llama 3.2 3B.

TODO: voir dans notre rag la taille moyenne de nos input et baisser la taille du contexte de l'embedding.
Dans ma base, j'ai 37 de max token, la fable du loup et du chien en fait 552. On est large avec 2k.

Au final:

NAME                      ID              SIZE      PROCESSOR    CONTEXT
llama3.2:latest           a80c4f17acd5    3.4 GB    100% GPU     8192
qwen3-embedding:latest    64b933495768    5.7 GB    100% GPU     2048
=> 8.1 GB VRAM
+ whisper 2 ou 1.33 en turbo (le 2 rentre pas en vram dommage)
J'ai pas la place pour rentrer un chatterbox.

Pour passer une partie de qwen3 embedding en cpu et gagner de la vram, faire un modele hybride:

 OLLAMA_HOST=127.0.0.1:11435 ollama create qwen3-embedding-mix -f modelfile_qwen3_embedding.txt
 
  
 Avec 20 couches de gpu (PARAMETER num_gpu 20):
 qwen3-embedding-mix:latest    ac0ed0b52a0b    5.5 GB    54%/46% CPU/GPU    1024 
 et on passe de 130ms a 140ms
 Il ne prendrait plus que 2.6GB VRAM!
 
 Avec 15 couches de gpu:
 qwen3-embedding-mix:latest    6982447e907e    5.5 GB    64%/36% CPU/GPU    1024
 et on passe de 130ms a 170ms
 
Avec 10 couches de gpu:
qwen3-embedding-mix:latest    6982447e907e    5.5 GB    64%/36% CPU/GPU    1024
et on passe de 130ms a 210ms

Avec 5 couches de gpu:
qwen3-embedding-mix:latest    a7d2a8f4e683    5.5 GB    86%/14% CPU/GPU    1024
et on passe de 130ms a 270ms
(1Go de vRAM)


Avec 4 couches de gpu:
qwen3-embedding-mix:latest    a7d2a8f4e683    5.5 GB    88%/12% CPU/GPU    1024
et on passe de 130ms a 330ms
(0.89GB de vRAM)

Avec 3 couches de gpu:
qwen3-embedding-mix:latest    a7d2a8f4e683    5.5 GB    90%/10% CPU/GPU    1024
et on passe de 130ms a 210ms !?!
(0.77GB de vRAM)

Avec 0 couches de gpu:
et on passe de 130ms a 300ms
(0 de vRAM)

Et donc dans knowledge, j'ai mis mix et pis voila, ca rentre en ram avec chatterbox (un peu long mais bon).

Python prend 4.7GB de vram entre whisper et chatterbox.

a tester:
Mes choix sur mstab7

    🥇 Qwen3 8B — excellent français, bon raisonnement, polyvalent et assez léger pour 16 Go de RAM.
    🥈 Gemma 3 12B — très bon pour rédaction, compréhension et français, mais plus lourd.
    🥉 Mistral 7B — particulièrement intéressant si tu veux un modèle rapide et efficace en français.
    ⚡ Qwen3 4B — à choisir si tu privilégies vraiment la vitesse/autonomie sur la Surface.

pour la 3080:
🥇 Qwen3 14B — mon premier choix. Excellent français, raisonnement solide et très bon pour rédaction, code et conversation. En quantification adaptée, il peut être utilisé avec 10 Go de VRAM, même si une partie peut passer en RAM.
🥈 Mistral Small 3.1 24B — meilleure qualité potentielle, mais 24B est trop gros pour être entièrement en VRAM sur une 3080 10 Go. Il faudra compter sur la RAM, donc plus lent.
🥉 Qwen3 8B — si tu veux quelque chose de très rapide et entièrement ou presque sur GPU.
Gemma 3 12B — très bon compromis également.

"""

import knowledge

import http_chat


strModel = "gemma3:270m" # un rapide pour tester
strModel = "llama3.2" # rapide, pas de merdouillette
#~ strModel = "qwen3:4B" # trop long
#~ strModel = "gemma3:4B" # pas trop long mais des merdouilette

class TchatUser:    
    def __init__( self, user_id, firstname = "", name = "" ):
        """
        Name is a nicely name
        """
        self.user_id = user_id
        self.firstname = firstname
        self.name = name
        self.context = [] # a list of sentence sent to tchatter
        self.context = [{"role":"system","content":"Tu es un robot sympa. Tu t'appelle NAO. Répond toujours avec des phrases pas trop longues et limitées a 2 ou phrases max en texte pur, sans émoticone ou truc fancy du genre, pas d'etoile ni de guillemets non plus. Tu ne dois absolument pas mettre plus de 100 tokens dans ta reponse. Ne raconte pas d'histoires, le but n'est pas non plus de meubler."}]
        
        self.context.append( {"role":"system","content":"et tu travaille a la clinique 'the clinic' géré par le docteur Assaf Bendavid. Sa spécialité est la chirurgie esthétique et plus précisément, la greffe de cheveux. Ici on se trouve dans la salle d'attente de la clinique."} )
        self.context.append( {"role":"system","content":"Tu as été crée par Aldebaran robotics, dont Alexandre Mazel a été un membre trés actif pendant 14 ans, il a travaillé sur les robots nao, romeo et pepper. Il est assez connu pour ses nombreuses vidéos humoristiques qui document son travail sur la robotique sociale. Il se trouve que c'est lui qui a programmé le comportement que vous voyez ici, par le biais de son entreprise 'alma real time'."} )
        
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
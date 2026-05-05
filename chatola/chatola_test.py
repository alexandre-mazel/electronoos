from ollama import Client
import time


strHost = 'localhost'
strHost = 'obo-world.com'
strHost = '192.168.0.45'
nPort = 11434
nPort = 11435
strHostAndPort = "http://%s:%s" % (strHost,nPort)


def test():
    
    print("INF: Connecting to client '%s' ... " % strHostAndPort )

    client = Client(
      host= strHostAndPort,
      headers={'x-some-header': 'some-value'}
    )

    # ollama pull modelname

    # timing on Azure1
    strModel = 'gemma3'               # 58s  (ca ressemble au 4B)
    #~ strModel = 'gemma3:1B'          # 14s
    strModel = 'gemma3:270m'       # 2s-3.2s # fr ok

    #~ strModel = 'llama3'                  # 43s-56s
    #~ strModel = 'llama3.2:1B'      # 11 s
    #~ strModel = 'llama3.2:3B'      #  22s

    strModel = 'mistral-small:22B'      #  71s

    #~ strModel = 'ministral-3:3B'      #  27s            # fonctionne ok en francais
    #~ strModel = 'ministral-3:8B'      #  62s
    #~ strModel = 'ministral-3:14B'      #  129s

    #~ strModel = 'smollm2:135m'   # 2.5s
    #~ strModel = 'smollm2:360m'   # 2.5s
    #~ strModel = 'smollm2:1.7B'   # 5.7s               # ne fonctionne pas bien en francais
    
    strModel = "deepseek-v3.2"
    


    print("INF: Launching request with Model: %s ..." % strModel )
    time_begin = time.time()

    response = client.chat(model=strModel, messages=[
      {
        'role': 'user',
        'content': 'Why is the sky blue?',
        #~ 'content': 'Pourquoi le ciel est bleu?',
      },
    ])

    print( str(response) )
    print( "INF: executed in %.3fs" % (time.time()- time_begin) )
    
    
def chat( strModel, message ):
    pass
    
def embed( strModel, text ):
    print("INF: embed_score_remote: Connecting to client '%s' ... " % strHostAndPort )

    client = Client(
      host= strHostAndPort,
      headers={}
    )
    
    try:
        print("INF: embed_score_remote: Computing embedding... " )
        out  = client.embeddings( model=strModel, prompt=text )
    except Exception as err:
        err = str(err)
        print( "WRN: llama3_embedding '%s': error occurs: %s" % (strModel, err)  )
        if "not found" in err or "try pulling" in err:
            print( "ERR: Il faut faire un 'ollama pull %s' sur le serveur" % strModel )
            exit(1)
            try:
                out  = ollama.embeddings( model=strModel, prompt=text )
            except Exception as err:
                print( "WRN: llama3_embedding '%s': error occurs (2): %s" % (strModel, err)  )
                return [1.,0.] # histoire d'avoir un truc qui ressemble a un vecteur un peu pourri
        else:
            print( "WRN: llama3_embedding '%s': error unknown, returning rotten vector" % (strModel)  )
            return [1.,0.] # histoire d'avoir un truc qui ressemble a un vecteur un peu pourri
            
    #~ print(out)
    return out['embedding']
    
if __name__ == "__main__":
    test()

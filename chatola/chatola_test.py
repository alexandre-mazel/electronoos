from ollama import Client
import time


strHost = 'localhost'
strHost = 'obo-world.com'
strHost = '192.168.0.45'
nPort = 11434
nPort = 11435
strHostAndPort = "http://%s:%s" % (strHost,nPort)


"""
Conso:

power.draw [W]
27.70 W
27.80 W
28.06 W
37.37 W
29.56 W
...
28.79 W
27.79 W
27.56 W
27.60 W
32.15 W
82.78 W
125.07 W
131.01 W
127.10 W
122.58 W
122.72 W

# kill x:
sudo systemctl stop gdm3

# pour le lancer:
(export OLLAMA_HOST=0.0.0.0:11435 && export OLLAMA_NO_CLOUD=1 && export OLLAMA_CONTEXT_LENGTH=8192 && ollama serve)

spci -vv -s 00:01.0
...
                LnkCap: Port #2, Speed 8GT/s, Width x16, ASPM L0s L1, Exit Latency L0s <256ns, L1 <8us
                        ClockPM- Surprise- LLActRep- BwNot+ ASPMOptComp+
...
                LnkSta: Speed 2.5GT/s (downgraded), Width x16 (ok)
                        TrErr- Train- SlotClk+ DLActive- BWMgmt+ ABWMgmt+
...                        
                LnkCtl: ASPM Disabled; RCB 64 bytes Disabled- CommClk+
                        ExtSynch- ClockPM- AutWidDis- BWInt- AutBWInt-

a@champion1:~$ sudo lspci -vv -s 00:01.0 | grep -E "LnkCap|LnkCtl|LnkSta"
                LnkCap: Port #2, Speed 8GT/s, Width x16, ASPM L0s L1, Exit Latency L0s <256ns, L1 <8us
                LnkCtl: ASPM Disabled; RCB 64 bytes Disabled- CommClk+
                LnkSta: Speed 2.5GT/s (downgraded), Width x16 (ok)
                LnkCtl2: Target Link Speed: 8GT/s, EnterCompliance- SpeedDis-
                LnkSta2: Current De-emphasis Level: -6dB, EqualizationComplete+, EqualizationPhase1+
                LnkCtl3: LnkEquIntrruptEn-, PerformEqu-


sudo nano /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash pcie_aspm=force"
=>
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
# puis:
sudo update-grub
sudo reboot

En fait le link etait bon:
watch -n 0.5 'cat /sys/bus/pci/devices/0000:01:00.0/current_link_speed'

Juste que quand la carte est en mode eco, le link ralentit pour economiser!
(argh 4h de recherche pour arriver la)

surveiller en continu: 
watch -n 1 'nvidia-smi --query-gpu=power.draw,pstate,utilization.gpu,memory.used --format=csv'

Avec timestamp et juste qd difference:
echo "timestamp            power limit pstate gpu mem vram"; prev=""; while true; do ts=$(date '+%Y-%m-%d %H:%M:%S'); v=$(nvidia-smi --query-gpu=power.draw,power.limit,pstate,utilization.gpu,utilization.memory,memory.used --format=csv,noheader,nounits | awk -F', ' '{printf "%3.0f %3.0f %5s %3.0f %3.0f %5.0f",$1,$2,$3,$4,$5,$6}'); if [ "$v" != "$prev" ]; then printf "%s  %s\n" "$ts" "$v"; prev="$v"; fi; sleep 1; done



"""

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

    strModel = 'mistral-small:22B'      #  71s # 61s sur Champion1

    #~ strModel = 'ministral-3:3B'      #  27s            # fonctionne ok en francais
    #~ strModel = 'ministral-3:8B'      #  62s
    #~ strModel = 'ministral-3:14B'      #  129s

    #~ strModel = 'smollm2:135m'   # 2.5s
    #~ strModel = 'smollm2:360m'   # 2.5s
    #~ strModel = 'smollm2:1.7B'   # 5.7s               # ne fonctionne pas bien en francais
    
    #~ strModel = "deepseek-v3.2"
    


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

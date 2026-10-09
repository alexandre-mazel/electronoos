import time
import requests

url = "http://engrenage.studio:45001/data" # mettre tchat pour tester un dialog et data pour juste un A/R.
payload = {"user_id": "test_speed", "msg": "coucou"}


print( "test sans session, puis avec session" )
session = None
for i in range( 4 ):
    start = time.perf_counter()
    if i < 2:
        response = requests.post(url, json=payload, timeout=10)
    else:
        print( "Using session!")
        if session == None:
            session = requests.Session() 
        response = session.post(url, json=payload, timeout=10)
    
    response.content # Consomme le corps pour liberer la connexion.
    
    headers_received = time.perf_counter()
    response_body = response.content
    end = time.perf_counter()

    print(f"Statut HTTP : {response.status_code}")
    print(f"Jusqu'aux en-tetes : {headers_received - start:.3f} s")
    print(f"Telechargement du corps : {end - headers_received:.3f} s")
    print(f"Temps total : {end - start:.3f} s")
    
    print( f"Connexion: {response.headers.get('Connection', 'keep-alive')}" )  # on a close donc session n'est pas optimise.
    # pourquoi ?
    # Si c'est un serveur Python base sur http.server, il peut y avoir:
    # self.close_connection = True
    # ou un en-tete ajoute explicitement :
    # self.send_header("Connection", "close")
        
    print("")


"""
RPI:
Statut HTTP : 200
Jusqu'aux en-tetes : 3.405 s
Telechargement du corps : 0.000 s
Temps total : 3.405 s
"""

"""
curl -4 -sS -o /dev/null -w \
'DNS=%{time_namelookup}s TCP=%{time_connect}s TLS=%{time_appconnect}s TTFB=%{time_starttransfer}s TOTAL=%{time_total}s\n' \
http://engrenage.studio:45001/tchat

#rpi:
DNS=3.069495s TCP=3.070283s TLS=0.000000s TTFB=3.073380s TOTAL=3.073974s
(pb de DNS donc, et apres 2 appel, il devrait etre en cache!)

PB: sur rpi: /etc/resolv.conf commencer par un 192.168.0.254, alors que ma box est en .100.
nameserver 192.168.0.254
nameserver 212.27.40.240
nameserver fd0f:ee:b0::1

Mais le fichier est regenere par network manager.

nmcli connection show --active

Wired connection 1  61d261f2-0b49-3a7e-9334-fe53cdcae2b9  ethernet  eth0 => celui la
docker0             ee3aec3d-a546-437d-b6ab-9b79537a2dc9  bridge    docker0
lo                  8b6fb253-0042-4241-af2f-c0ade9806b5b  loopback  lo

sudo nmcli connection modify "Wired connection 1" ipv4.dns "192.168.0.100,212.27.40.240" ipv4.ignore-auto-dns yes
sudo systemctl restart NetworkManager

et maintenant:
Statut HTTP : 200
Jusqu'aux en-tetes : 0.241 s
Telechargement du corps : 0.000 s
Temps total : 0.241 s

et curl:
DNS=0.001307s TCP=0.002101s TLS=0.000000s TTFB=0.005166s TOTAL=0.005744s

"""



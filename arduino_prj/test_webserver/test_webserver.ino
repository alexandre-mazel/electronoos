// Ces deux bibliothèques sont indispensables pour le shield
#include <SPI.h>
#include <Ethernet.h>

#define ETH_CS_PIN      53

// L'adresse MAC du shield
byte mac[] = { 0x90, 0xA2, 0xDA, 0x0E, 0xA5, 0x7E };
// L'adresse IP que prendra le shield
//IPAddress ip(192,168,0,143);
IPAddress ip(169, 254, 199, 55);
IPAddress subnet(255,255,0,0);
IPAddress gateway(169, 254, 199, 55);
IPAddress dns(169, 254, 199, 55);


// Initialise notre serveur
// Ce dernier écoutera sur le port 4200
EthernetServer serveur(80);

void setup()
{
  // On démarre la voie série pour déboguer
  Serial.begin(1000000);

  char erreur = 0;
  // On démarre le shield Ethernet SANS adresse IP (donc donnée via DHCP)
  erreur = Ethernet.begin(mac);
  Ethernet.init(ETH_CS_PIN);

  if (erreur == 0) {
    Serial.println("Parametrage avec ip fixe...");
    // si une erreur a eu lieu cela signifie que l'attribution DHCP
    // ne fonctionne pas. On initialise donc en forçant une IP
    Ethernet.begin(mac, ip,dns,gateway,subnet);
  }

  Serial.print("Static IP        : "); Serial.println(Ethernet.localIP());
  
  Serial.println("Init...");
  // Donne une seconde au shield pour s'initialiser
  delay(1000);
  // On lance le serveur
  serveur.begin();
  Serial.print("Pret !");
}

void loop()
{
  // Regarde si un client est connecté et attend une réponse
  EthernetClient client = serveur.available();
  if (client) 
  {
    // Quelqu'un est connecté !
    Serial.print("On envoi !");
    // On fait notre en-tête
    // Tout d'abord le code de réponse 200 = réussite
    client.println("HTTP/1.1 200 OK");
    // Puis le type mime du contenu renvoyé, du json
    client.println("Content-Type: application/json");
    // Et c'est tout !
    // On envoie une ligne vide pour signaler la fin du header
    client.println();

    // Puis on commence notre JSON par une accolade ouvrante
    client.println("{");
    // On envoie la première clé : "uptime"
    client.print("\t\"uptime (ms)\": ");
    // Puis la valeur de l'uptime
    client.print(millis());
    //Une petite virgule pour séparer les deux clés
    client.println(",");
    // Et on envoie la seconde nommée "analog 0"
    client.print("\t\"analog 0\": ");
    client.println(analogRead(A0));
    // Et enfin on termine notre JSON par une accolade fermante
    client.println("}");
    // Donne le temps au client de prendre les données
    delay(10);
    // Ferme la connexion avec le client
    client.stop();
  }
}
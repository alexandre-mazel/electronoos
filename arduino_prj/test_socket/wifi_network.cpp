#include "wifi_network.hpp"
#include "eeprom_prefs.hpp"


// Enter your WiFi SSID and password
char ssid[] = "Liberte";              // your network SSID (name)
char pass[32] = "la...";                // your network password (use for WPA, or use as key for WEP) - read from rom - assume enought space to store it!
int keyIndex = 0;                     // your network key Index number (needed only for WEP)

const char * pCurrentSSID = ssid;
int bModeIsAP = 0;

int status = WL_IDLE_STATUS;
// if you don't want to use DNS (and reduce your sketch size)
// use the numeric IP instead of the name for the server:
//IPAddress server(74,125,232,128);  // numeric IP for Google (no DNS)

char dataserver_hostname[] = "engrenage.studio";    // name address for the server
char dataserver_hostname_mirror[] = "192.168.0.50";    // local in case of no external internet
char dataserver_path[]   = "/record_data.py";

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
WiFiClient wifi_client; // ici il ne faudrait pas le creer quand on est en mode server, mais j'ai pas trop vu la difference
//int bDisconnected = false;

void scanNetworks()
{
  Serial.println("scan start");

  // WiFi.scanNetworks will return the number of networks found
  int n = WiFi.scanNetworks();
  Serial.println("scan done");
  if (n == 0) {
      Serial.println("no networks found");
  } else {
    Serial.print(n);
    Serial.println(" networks found");
    for (int i = 0; i < n; ++i) {
      // Print SSID and RSSI for each network found
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.print(")");
      Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN)?" ":"*");
      delay(10);
    }
  }
  Serial.println("");
}



void retrievePassFromEeprom(char * password)
{
  // pass is written to eeprom in the first chars (padded with \0)
  // ASSUME: password is an already allocated area with enough chars !
  
  
  // first time, call once to write your SSID:
  //writeStringToEeprom( 100,"***" );

  // dumpEeprom(); // to help debug

  // read it back
  readStringFromEeprom( 100, password );
  int nLen = strlen(password);
  Serial.print("DBG: retrievePassFromEeprom: readed password has a length of ");
  Serial.print(nLen);
  if( nLen == 0 )
  {
    Serial.println();
  }
  else
  {
    Serial.print(", first char is '");
    Serial.print(password[0]);
    Serial.print("', and last is '");
    Serial.print(password[nLen-1]);
    Serial.println("'");
  }
}


void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

int connectToWifi( void )
{
  // Set WiFi to station mode and disconnect from an AP if it was previously connected
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  // scanNetworks(); // nice to debug but takes some seconds

  retrievePassFromEeprom(pass);

  // attempt to connect to Wifi network:
  Serial.print("Attempting to connect to SSID: "); // 2.5s for Liberte
  Serial.println(ssid);

  WiFi.begin(ssid, pass);
  int cpt = 0;
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
      ++cpt;
      if( cpt > 10 ) // 5 sec
      {
        Serial.println("\nConnection failed.");
        return 0;
      }
  }

  Serial.println("\nConnected to WiFi");
  printWifiStatus();
  bModeIsAP = 0;

  return 1;
}

int createWifiAP( const char* SSID, const char* password )
{
  Serial.print("INF: createWifiAP: Setting Access Point with SSID: "); Serial.println( SSID );

  WiFi.mode( WIFI_AP );

  // Remove the password parameter, if you want the AP (Access Point) to be open
  const int channel = 10; // At home it's better on channel 1
  const int ssid_hidden = 0; // 1 for true
  const int max_connection = 1;
  WiFi.softAP(SSID, password, channel, ssid_hidden, max_connection);

  IPAddress IP = WiFi.softAPIP();
  Serial.print( "INF: createWifiAP: Channel: " ); Serial.print( channel ); Serial.print( ", Access Point IP address: "); Serial.println(IP);

  //byte encryption = WiFi.encryptionType();
  //Serial.print( "Encryption Type: " ); Serial.println( encryption, HEX );

  pCurrentSSID = SSID; // TODO: Crado should copy it, as one day it can appear this char* isn't temporary
  bModeIsAP = 1;

  return 1;
}

const char * getCurrentIP( void )
{
  static char sz_ip[4*3+3+1];
  IPAddress IP = WiFi.softAPIP();
  if(!bModeIsAP)
    IP = WiFi.localIP();
  // return (const char*)IP;
  //const uint8_t* tip = IP.raw_address();
  //sprintf( sz_ip, "%d.%d.%d.%d", tip[0], tip[1],tip[2],tip[3] );
  sprintf( sz_ip, "%d.%d.%d.%d", IP[0], IP[1],IP[2],IP[3] );
  return sz_ip;
  
}

const char * getCurrentSSID( void )
{
  return pCurrentSSID;
}

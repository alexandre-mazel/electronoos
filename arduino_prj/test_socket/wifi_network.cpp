#include "wifi_network.hpp"

#define USE_PREFS // Pref is the new things of esp32

#ifdef USE_PREFS
#   include <Preferences.h>
    Preferences prefs;
#else
#    include <EEPROM.h>
#endif // USE_PREFS


void writeStringToEeprom(int nOffsetStart, const char* s)
{
  // write until a '\0' is found in the string

  int nWritten = 0;

#ifdef USE_PREFS
    prefs.begin("Eeprom"); // a sort of namespace
    nWritten = strlen(s);
    prefs.putBytes("Eeprom_mykey",s,nWritten);  // keyname here for compatibility, but it's intended to be a key to have different variables)
#else
  const char * p = s;
  while( *p )
  {
    EEPROM.write(nOffsetStart, *p); // update: write only if different (save a bit of ageing) - changed to write as update seems to be not available
    ++nOffsetStart;
    ++p;
  }
  EEPROM.write(nOffsetStart, *p); // write the null

  EEPROM.commit(); // needed with ESP32 // yes but no => use Prefs

  nWritten = int(p-s);
#endif

  Serial.print("DBG: writeStringToEeprom: written to eeprom: ");
  Serial.print( nWritten );
  Serial.println(" char(s)");
}

void readStringFromEeprom(int nOffsetStart, char* s)
{
  int nReaded = 0;

  // read until a '\0' is found in Eeprom
#ifdef USE_PREFS
    prefs.begin("Eeprom");
    nReaded = prefs.getBytesLength("Eeprom_mykey");
    prefs.getBytes("Eeprom_mykey",s,nReaded);
#else
  char * p = s;
  while( 1 )
  {
    char c = EEPROM.read(nOffsetStart);
    *p = c;
    ++nOffsetStart;
    ++p;
    Serial.println((int)c,HEX);
    if( c == '\0' )
    {
      break;
    }
    nReaded = int(p-s);
  }
#endif

Serial.print( "DBG: readStringFromEeprom: readed from eeprom: " );
Serial.print( nReaded );
Serial.println( " char(s)" );

}


// Enter your WiFi SSID and password
char ssid[] = "Liberte";              // your network SSID (name)
char pass[32] = "la...";                // your network password (use for WPA, or use as key for WEP) - read from rom - assume enought space to store it!
int keyIndex = 0;                     // your network key Index number (needed only for WEP)

int status = WL_IDLE_STATUS;
// if you don't want to use DNS (and reduce your sketch size)
// use the numeric IP instead of the name for the server:
//IPAddress server(74,125,232,128);  // numeric IP for Google (no DNS)

char server_hostname[] = "engrenage.studio";    // name address for the server
char server_hostname_mirror[] = "192.168.0.50";    // local in case of no external internet
char path[]   = "/record_data.py";

// Initialize the Ethernet client library
// with the IP address and port of the server
// that you want to connect to (port 80 is default for HTTP):
WiFiClient wifi_client;
int bDisconnected = false;

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
  writeStringToEeprom( 0,"lagrosseliberte666!" );

  // dumpEeprom(); // to help debug

  // read it back
  readStringFromEeprom( 0, password );
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
  /* return 1 on success */

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
  while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
  }

  Serial.println("");
  Serial.println("Connected to WiFi");
  printWifiStatus();

  return 1;
}

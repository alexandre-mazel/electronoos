#ifndef __WIFI_NETWORK_H__
#define __WIFI_NETWORK_H__

#include <WiFi.h>

extern WiFiClient wifi_client;

extern char dataserver_hostname[];    // name address for the server
extern char dataserver_hostname_mirror[];    // local in case of no external internet
extern char dataserver_path[];

int connectToWifi( void );

int createWifiAP( const char* SSID, const char* password = NULL ); // Leave NULL for no password

const char * getCurrentIP( void );

#endif
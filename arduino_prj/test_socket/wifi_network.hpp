#ifndef __WIFI_NETWORK_H__
#define __WIFI_NETWORK_H__

#include <WiFi.h>

extern WiFiClient wifi_client;
int connectToWifi( void );

int createWifiAP( const char* SSID, const char* password = NULL ); // Leave NULL for no password

#endif
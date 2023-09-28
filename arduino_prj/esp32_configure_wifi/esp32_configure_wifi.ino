#include <WiFi.h>

const char* ssid = "Liberte";
const char* password = "lagrosseliberte666!"; // to do: write it in rom once then load it from rom

String hostname = "ESP32_Alex";

/*
Use wifi multi to connect to the strongest from a long list

#include <WiFiMulti.h>

WiFiMulti wifiMulti;

// WiFi connect timeout per AP. Increase when connecting takes longer.
const uint32_t connectTimeoutMs = 10000;

void setup(){
  Serial.begin(115200);
  delay(10);
  WiFi.mode(WIFI_STA);
  
  // Add list of wifi networks
  wifiMulti.addAP("ssid_from_AP_1", "your_password_for_AP_1");
  wifiMulti.addAP("ssid_from_AP_2", "your_password_for_AP_2");
  wifiMulti.addAP("ssid_from_AP_3", "your_password_for_AP_3");
  

*/

void get_network_info(){
    if(WiFi.status() == WL_CONNECTED) {
        Serial.print("[*] Network information for ");
        Serial.println(ssid);

        Serial.println("[+] BSSID : " + WiFi.BSSIDstr());
        Serial.print("[+] Gateway IP : ");
        Serial.println(WiFi.gatewayIP());
        Serial.print("[+] Subnet Mask : ");
        Serial.println(WiFi.subnetMask());
        Serial.println((String)"[+] RSSI : " + WiFi.RSSI() + " dB");
        Serial.print("[+] ESP32 IP : ");
        Serial.println(WiFi.localIP());
    }
}

String get_wifi_status(int status){
    switch(status){
        case WL_IDLE_STATUS:
        return "WL_IDLE_STATUS";
        case WL_SCAN_COMPLETED:
        return "WL_SCAN_COMPLETED";
        case WL_NO_SSID_AVAIL:
        return "WL_NO_SSID_AVAIL";
        case WL_CONNECT_FAILED:
        return "WL_CONNECT_FAILED";
        case WL_CONNECTION_LOST:
        return "WL_CONNECTION_LOST";
        case WL_CONNECTED:
        return "WL_CONNECTED";
        case WL_DISCONNECTED:
        return "WL_DISCONNECTED";
    }
}


void setup(){
    Serial.begin(115200);
    delay(1000);

    WiFi.mode(WIFI_STA); //Optional

    // pour demandé une ip fixe:
    if(1)
    {
      IPAddress ip(192, 168, 0, 132); // l'ip qu'on veut
      IPAddress dns(192, 168, 0, 1);
      IPAddress gateway(192, 168, 0, 100); // ip de la box, (eg check dans la connection précédente sans ip fixe)
      IPAddress subnet(255, 255, 255, 0);

      Serial.print("DBG Forcing IP fixe");
      WiFi.config(ip, gateway, subnet, dns);
    }

    // set a specific hostname: WiFi.setHostname(hostname.c_str()); //define hostname

    WiFi.begin(ssid, password);
    Serial.println("\nConnecting");

    while(WiFi.status() != WL_CONNECTED){
        Serial.print(".");
        delay(100);
    }

    Serial.println("\nConnected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
    get_network_info();

    //WiFi.disconnect(); // if you want to disconnect, then WiFi.reconnect();
}

void sendInfoToRpi(void)
{
  WiFiClient client;
  if (!client.connect("192.168.0.11", 1032)) 
  {
   Serial.println("Connection to host failed");
  }
  client.print("Hello from ESP32!");
  client.stop();
}

void loop()
{
   delay(5000);
   return;
}
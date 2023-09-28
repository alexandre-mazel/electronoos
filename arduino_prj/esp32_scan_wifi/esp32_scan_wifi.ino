#include "WiFi.h"

String get_encryption_type(wifi_auth_mode_t encryptionType) {
    switch (encryptionType) {
        case (WIFI_AUTH_OPEN):
            return "Open";
        case (WIFI_AUTH_WEP):
            return "WEP";
        case (WIFI_AUTH_WPA_PSK):
            return "WPA_PSK";
        case (WIFI_AUTH_WPA2_PSK):
            return "WPA2_PSK";
        case (WIFI_AUTH_WPA_WPA2_PSK):
            return "WPA_WPA2_PSK";
        case (WIFI_AUTH_WPA2_ENTERPRISE):
            return "WPA2_ENTERPRISE";
    }
}

void setup(){
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);
}

char* intBufferToChar(const uint8_t * buf)
{
  // quick and dirty way to concert a buffer of short int to printable data
  const int nSizeBufMax = 128;
  static char bufConverted[nSizeBufMax];
  int i;
  int j = 0;
  for( i = 0; i < nSizeBufMax; ++i )
  {
    if( buf[i] == 0 || i >= nSizeBufMax/3)
      break;
    bufConverted[j] = '0' + buf[i]/10;
    ++j;
    bufConverted[j] = '0' + buf[i]%10;
    ++j;
    bufConverted[j] = ' ';
    ++j;
  }
  bufConverted[j] = '\0';
  return bufConverted;
}

void loop() {
    Serial.println("WiFi Scan Demo");
    Serial.println("[*] Scanning WiFi network");

        // WiFi.scanNetworks will return the number of networks found
        int n = WiFi.scanNetworks(false,true,false); // (bool async = false, bool show_hidden = false, bool passive = false, uint32_t max_ms_per_chan = 300, uint8_t channel = 0, const char * ssid=nullptr, const uint8_t * bssid=nullptr);
        Serial.println("[*] Scan done");
        if (n == 0) {
            Serial.println("[-] No WiFi networks found");
        } else {
            Serial.println((String)"[+] " + n + " WiFi networks found\n");
            for (int i = 0; i < n; ++i) {
                // Print SSID, RSSI and WiFi Encryption for each network found
                Serial.print(i + 1);
                Serial.print(": ");
                Serial.print(WiFi.SSID(i));
                Serial.print(" (");
                Serial.print(WiFi.RSSI(i));
                Serial.print(" dB) [");
                Serial.print(get_encryption_type(WiFi.encryptionType(i))); // Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN)?" ":"*");
                Serial.print("] [");
                Serial.print(intBufferToChar(WiFi.BSSID(i)));
                Serial.println("]");
                delay(10);
            }
        }
        Serial.println("");

        // Wait a bit before scanning again
        if(1)
        {
          delay(10000);
        }
        else
        {
          // deep sleep (ennuyeux car fait new device dans windows chaque 10 sec)
          esp_sleep_enable_timer_wakeup(30 * 1000000);
          esp_deep_sleep_start();
        }
}
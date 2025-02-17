#include <arduino.h>
#include "wifi_network.hpp"

const int ledPin = 13;

void setup()
{
  Serial.begin(115200);

  pinMode( ledPin, OUTPUT );

  Serial.println ("" );
  Serial.println( "test_socket v0.6" );

  connectToWifi();

}

const char * host = "192.168.0.46"; // "192.168.0.50", "192.168.0.46"
const uint16_t port = 8090;

int nbr_loop = 0;

void loop() 
{
  Serial.print( "INF: Connecting to " ); Serial.print( host ); Serial.print( ":" ); Serial.println( port ); 
  Serial.print( "INF: nbr_loop: " ); Serial.println( nbr_loop );

  digitalWrite(ledPin, HIGH);

  if ( !wifi_client.connect(host, port) ) 
  {
    Serial.println( "Connection to host failed" );

    delay(3*1000);
    return;
  }
  Serial.println( "Connected to server successful!" );

  Serial.println( "Sending data!" );
  /*
  for( int i = 0; i < 100; ++i )
  {
    wifi_client.print( "Hello from ESP32!" );
  }
  */

  const int nSizeBuffer = 5000;

  unsigned char buf[nSizeBuffer];
  for( int j = 0; j < nSizeBuffer; ++j )
  {
    buf[j] = j%100;
  }

  for( int i = 0; i < 100*100*30; ++i )
  {
    wifi_client.write((unsigned char*)buf,nSizeBuffer);  
    // wifi_client.write((unsigned char)(i%100));
  
    //delay(10); // 100 bytes per sec
    if( (nbr_loop % 2) == 0 )
    {
      if( !wifi_client.connected() )
      {
        Serial.println( "ERR: Server lost!" );
        break;
      }
    }
  }

  Serial.println( "Disconnecting..." );
  wifi_client.stop();
  digitalWrite(ledPin, LOW);
  delay(10*1000);
  nbr_loop += 1;
}
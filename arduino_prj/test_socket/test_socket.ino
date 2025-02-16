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

const char * host = "192.168.0.46";
const uint16_t port = 8090;

void loop() 
{
  Serial.print( "INF:Connecting to " ); Serial.print( host ); Serial.print( ":" ); Serial.println( port ); 

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
  for( int i = 0; i < 100*100*30; ++i )
  {
    // here test he's still connected (or so need to reconnect)
    wifi_client.write((unsigned char)(i%100));
    //delay(10); // 100 bytes per sec
    if( 1 )
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
  delay(10*1000);
}
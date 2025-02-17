#include <arduino.h>
#include "wifi_network.hpp" // lien symbolique vers le hpp ( creer en lancant un cmd en mode administrateur et la commande: mklink wifi_network.cpp ..\test_socket\wifi_network.cpp )
#include "misbkit.hpp"

const int ledPin = 13;


const uint16_t port = 8090;
WiFiServer server( port );

void start_server( void )
{
  Serial.print( "INF: start_server: Starting server on port " ); Serial.println( port );
  server.begin();
}

void update_server( void )
{
  WiFiClient client = server.available();   // Listen for incoming clients

  if (client)  // If a new client connects,
  {                             
    Serial.println("INF: update_server: New Client.");        // print a message out in the serial port
    String currentLine = "";              // make a String to hold incoming data from the client
    while( client.connected() )            // loop while the client's connected
    {
      while( client.available() )             // if there's bytes to read from the client,
      {             
        char c = client.read();           // read a byte, then
        Serial.write(c);                  // print it out the serial monitor

        currentLine += c;
      }

      if( currentLine.equals( "hello" ) )
      {
        Serial.println( "" );
        client.write( "Hello to you!" );
        currentLine = "";
      }
      else if( strncmp( currentLine.c_str(), "Motor", 5 ) == 0 )
      {
        Serial.println( "" );
        Serial.println( "INF: Motor position received, sending current one" );
        client.write( 100 );
        currentLine = "";
      }
    }

    // Close the connection
    client.stop();
    Serial.println( "INF: update_server: Client disconnected." );
    Serial.println( "" );
  }
}

void setup()
{
  Serial.begin(115200);

  pinMode( ledPin, OUTPUT );

  Serial.println ("" );
  Serial.println( "serv_socket v0.6" );

  // connectToWifi();
  createWifiAP( getArduinoId() );

  start_server();
}


void loop() 
{

  update_server();

}
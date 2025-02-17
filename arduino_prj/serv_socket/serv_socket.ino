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

  if( client )  // If a new client connects,
  {                             
    Serial.println("INF: update_server: New Client.");        // print a message out in the serial port
    long int time_begin = millis();
    long int nbr_received = 0;
    long int nbr_sent = 0;

    //String currentLine = "";              // make a String to hold incoming data from the client
    const int nMaxCurrentLine = 512;
    char currentLine[nMaxCurrentLine+1];
    int nLenCurrentLine = 0;
    while( client.connected() )           // loop while the client's connected
    {
      /*
      if(0)
      {
        while( client.available() )         // if there's bytes to read from the client,
        {             
          char c = client.read();           // read a byte, then
          // Serial.write(c);               // print it out the serial monitor

          currentLine += c;
          nbr_received += 1;
        }
      }
      else
      {
        // currentLine is String
        const int nSizeBuffer = 10;
        unsigned char buf[nSizeBuffer];
        int nReaded = client.read( (unsigned char*)buf, nSizeBuffer );
        if(nReaded > 0)
        {
          //Serial.print( "DBG: nReaded: " ); Serial.println( nReaded );
          for( int i = 0; i < nReaded; ++i )
          {
            currentLine += (char)buf[i];
          }
          nbr_received += nReaded;
          // Serial.println( currentLine.c_str() );
        }
      }
      */
      {
        // currentLine is char *
        const int nSizeBuffer = 20;
        char buf[nSizeBuffer];
        int nReaded = client.read( (unsigned char*)buf, nSizeBuffer );
        if(nMaxCurrentLine < nLenCurrentLine+nReaded)
        {
          nReaded = nMaxCurrentLine - nLenCurrentLine;
          Serial.print( "WRN: Overflow in line reading !" );
        }
        if(nReaded > 0)
        {
          //Serial.print( "DBG: nReaded: " ); Serial.println( nReaded );
          strncpy( &(currentLine[nLenCurrentLine]), buf, nReaded );
          nLenCurrentLine += nReaded;
          currentLine[nLenCurrentLine] = '\0';

          nbr_received += nReaded;
          // Serial.println( currentLine );
        }
      }

      if( nLenCurrentLine > 0 )
      {
        //if( currentLine.equals( "Hello" ) )
        if( nLenCurrentLine == 5 && strcmp( currentLine, "Hello" ) == 0 )
        {
          Serial.println( "Received Hello!" );
          client.write( "Hello to you!" );
          //currentLine = "";
          nLenCurrentLine = 0;
          currentLine[nLenCurrentLine] = '\0'; // moche
        }
        //else if( strncmp( currentLine.c_str(), "Motor", 5 ) == 0 )
        else if( strncmp( currentLine, "Mot", 3 ) == 0 )
        {
          // Serial.println( "" );
          // Serial.println( "INF: Motor position received, sending current one" );
          client.write( 100 );
          nbr_sent += 1;
          //currentLine = "";
          nLenCurrentLine = 0;
          currentLine[nLenCurrentLine] = '\0'; // moche
        }
      }

      long int duration = millis() - time_begin;
      if( duration > 5000 )
      {
        float received = nbr_received / (float)duration;
        float sent = nbr_sent / (float)duration;
        Serial.print( "Received: " ); Serial.print( received, 3 ); Serial.print( "kB, Sent: " ); Serial.print( sent, 3 ); Serial.println( "kB" );
        time_begin = millis();
        nbr_received = 0;
        nbr_sent = 0;
      }

      delay( 2 ); // give back some time to the system // doesn't seem to change anything

      /*
      NTESTED:
      Place DoEvent(10) in your Loop()

      void DoEvents(int mils) {
        unsigned long currentMillis = millis();
        if (currentMillis + mils > 4294967295)
          delay(mils);
        else
          while ((currentMillis + mils) > millis()) {
            server.handleClient();
        yield();
        }
      }
*/

    } // while client connected

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
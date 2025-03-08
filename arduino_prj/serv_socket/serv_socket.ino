#include <arduino.h>
#include "wifi_network.hpp" // lien symbolique vers le hpp ( creer en lancant un cmd en mode administrateur et la commande: mklink wifi_network.cpp ..\test_socket\wifi_network.cpp )
#include "misbkit.hpp"
#include "dynamixel_motor.hpp"

const int ledPin = 13;


const uint16_t port = 8090;
WiFiServer wifi_server( port );

void start_server( void )
{
  Serial.print( "INF: start_server: Starting server on port " ); Serial.println( port );
  wifi_server.begin();
  wifi_server.setNoDelay(1); // test mais je suis pas sur que ca change qqchose
  Serial.print( "INF: start_server: server nodelay: " ); Serial.println( wifi_server.getNoDelay() );
}

unsigned char allMotorsPosition[6] = {100,101,102,103,104,105};

void update_server( void )
{
  WiFiClient client = wifi_server.available();   // Listen for incoming clients
  wifi_server.setNoDelay(1);

  if( client )  // If a new client connects,
  {                             
    Serial.println("INF: update_server: New Client.");       // print a message out in the serial port
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
      if( client.available() > 0 )
      {
        // currentLine is char *
        const int nSizeBuffer = 20;
        char buf[nSizeBuffer];
        int nReaded = client.read( (unsigned char*)buf, nSizeBuffer );

        if( nReaded > 0 )
        {
          if(nMaxCurrentLine < nLenCurrentLine+nReaded)
          {
            nReaded = nMaxCurrentLine - nLenCurrentLine;
            Serial.print( "WRN: Overflow in line reading !" );
          }

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
          if( 1 )
          {
            // send answer
            // client.write( 100 ); // just 1 motor value
            client.write( allMotorsPosition, 6 ); // all values
            nbr_sent += 1;
          }
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
            wifi_server.handleClient();
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

  Serial.println ( "" );
  Serial.println( "serv_socket v0.61" );

  if( 0 )
  {
    Serial.flush();
    delay(1000); // wait before crashing (in case of)...
    for( int i = 0; i < 5; ++i )
    {
      Serial.println("serv_socket v0.6: loop debug xiao");
      Serial.flush();
      delay(500);
    }
  }

  if( isMisBKit() )
  {
    pinMode( ledPin, OUTPUT ); // Attention cette ligne fait planter le XIAO C3 !!!
  }


  // coupe le BT (mais ne fonctionne pas)
//  esp_bluedroid_disable();
//  esp_bluedroid_deinit();
//  esp_bt_controller_disable();
//  esp_bt_controller_deinit();

  //connectToWifi();
  createWifiAP( getArduinoId() );


  start_server();

  // init motor
  scanMotors();
}


void loop() 
{
  update_server();
}
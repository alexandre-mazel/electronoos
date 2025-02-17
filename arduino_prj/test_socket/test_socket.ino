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

void sendData100(int nNumLoop )
{

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
    if( (nNumLoop % 2) == 0 )
    {
      if( !wifi_client.connected() )
      {
        Serial.println( "ERR: Server lost!" );
        break;
      }
    }
  }
}


void receiveData100(int nNumLoop )
{

  Serial.println( "INF: Receiving data!" );

  const int nSizeBuffer = 10;

  unsigned char nPrevData = 99;

  long int nLenDataReceived = 0;

  long int time_begin = millis();

  while( 1 )
  {
    while( wifi_client.available() < nSizeBuffer )
    {
      //Serial.println("Waiting for packet...");
      delay(0);
    }

    unsigned char buf[nSizeBuffer];
    int nReaded = wifi_client.read((unsigned char*)buf,nSizeBuffer);
    if( 0 )
    {
      Serial.print( "DBG: nReaded: " ); Serial.println( nReaded );
      for( int i = 0; i < 10; ++i )
      {
        Serial.print( i ); Serial.print(": " ); Serial.println( buf[i] );
      }
    }
    for( int i = 0; i < nReaded; ++i )
    {
      // Serial.print( i ); Serial.print(": " ); Serial.println( buf[i] );
      if ( ! ( buf[i] == nPrevData+1 || ( buf[i] == 0 && nPrevData == 99 ) ) )
      {
        Serial.print("ERR: data corrupted (nPrevData: "); Serial.println( nPrevData );
        wifi_client.flush(); // flush all
        break;
      }
      nPrevData = buf[i];
    }

    nLenDataReceived += nReaded;
    long int duration = millis() - time_begin;
    //Serial.println( duration );
    if( duration > 5000 )
    {
      long int throughput = (nLenDataReceived) / duration;
      Serial.print( "INF: throughput: "); Serial.print( throughput ); Serial.println( "kB/sec" );
      time_begin = millis();
      nLenDataReceived = 0;
    }
  }

}

const char * host = "192.168.0.50"; // rpi5: "192.168.0.50", msttab7: "192.168.0.46"
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

  //sendData100( nbr_loop );
  receiveData100( nbr_loop );

  Serial.println( "Disconnecting..." );
  wifi_client.stop();
  digitalWrite(ledPin, LOW);
  delay(10*1000);
  nbr_loop += 1;
}
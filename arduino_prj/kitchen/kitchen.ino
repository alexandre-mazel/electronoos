#include <EEPROM.h>

/*
 * La table des Aromes des Caves du Louvre
 * 
 * Version number: cf the message in the print of the setup function
 * Author: Alexandre Mazel
 * copyright (c) A.Mazel 2015
 
 * compiled with Arduino 1.0.6
 */

#include "Ai_WS2811.h"

const int nFirstLedPin = 53; // one led per reader
const int nNbrLeds = 90;
Ai_WS2811 ws2811;
struct CRGB * apLeds[1] = {NULL};

////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
void setup()
{
  int i;
  Serial.begin(9600);
  pinMode( nFirstLedPin, OUTPUT );

  ws2811.init(nFirstLedPin,nNbrLeds);
  apLeds[0] = (struct CRGB*)ws2811.getRGBData();
  ws2811.setDim( 1 );

  
  Serial.println( "\nArduino started: Kitchen v0.6\n" );
  
  Serial.print( "nFirstLedPin: " );
  Serial.println( nFirstLedPin, DEC );
}

int nFrame = 0;
void loop()
{
  int nCoef = 2;
  if( nFrame <= 255*nCoef )
  {
    ws2811.setColor( nFrame/nCoef, 0, 0 );
    ++nFrame;
  }
  delay(1);
}

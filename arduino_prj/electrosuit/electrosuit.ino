#include <EEPROM.h>

/*
 * La table des Aromes des Caves du Louvre
 * 
 * Version number: cf the message in the print of the setup function
 * Author: Alexandre Mazel
 * copyright (c) A.Mazel 2015
 */

#include <avr/pgmspace.h>
const char pad[3] PROGMEM = { 0, 0, 0 };


#include "Ai_WS2811.h"
//#include <../../../../libraries/EEPROM/EEPROM.h> // => generate error when in a .c

const int nNbrReader = 3;
const int nLenCode = 12;

const int nFirstLedPin = 50; // one led per reader
const int nFirstPresencePin = 40; // one pin per reader

const int nLedPinSendGood3 = 22;
const int nLedPinReceiveGood3 = 24;


#define NUM_PIXELS 48
Ai_WS2811 aWs2811[nNbrReader];
struct CRGB * apLeds[nNbrReader] = {NULL, NULL, NULL};

void check_leds( void )
{
  // check all leds are ok: make the led blink all once (for startup)
  Serial.println( "check_leds..." );
  int i;
  for( i = 0; i < nNbrReader; ++i )
  {
    aWs2811[i].setColor( 255, 0, 0 );
  }
  delay( 1000 );
  
  for( i = 0; i < nNbrReader; ++i )
  {
    aWs2811[i].setColor( 0, 255, 0 );    
  }
  delay( 1000 );  
  
  for( i = 0; i < nNbrReader; ++i )
  {
    aWs2811[i].setColor( 0, 0, 255 );
  }
  delay( 1000 );  

  for( i = 0; i < nNbrReader; ++i )
  {
    aWs2811[i].setColor( 0, 0, 0 );
  }

}




////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
void setup()
{
  pad[0];
  int i;
  Serial.begin(9600);
  // setup pin
  for( i = 0; i < nNbrReader; ++i )
  {
    pinMode( nFirstLedPin+i, OUTPUT );
  }

  for( i = 0; i < nNbrReader; ++i )
  {
    aWs2811[i].init(nFirstLedPin+i,NUM_PIXELS);
    apLeds[i] = (struct CRGB*)aWs2811[i].getRGBData();
    aWs2811[i].setDim( 1 );
  }
//  aWs2811[2].reducePixelNumber( 4 );  
  
  
  //check_leds();

  
  Serial.println( "\nArduino started: ElectroSuit v0.6\n" );
}

int nFpsCpt = 0;
unsigned long timeFpsBegin;

int nNumFrame = 0;
int nNumSequence = 0;
void loop()
{
  if( nNumFrame >= 11 )
  {
    nNumFrame = 0;
    ++nNumSequence;
    if( (nNumSequence % 2 == 1) )
    {
      delay( 1000 );
    }
  }
  aWs2811[0].setOneBrightOtherLow( 8, 0, nNumFrame-1, 255,255,255 );
  aWs2811[0].setOneBrightOtherLow( 10, 8, 10-nNumFrame, 255,255,255 );
  aWs2811[0].setOneBrightOtherLow( 11, 18, nNumFrame, 255,255,255 );
  aWs2811[0].setOneBrightOtherLow( 10, 29, (10-nNumFrame)-1, 255,255,255 );
  aWs2811[0].setOneBrightOtherLow( 4, 39, nNumFrame, 255,255,255 );  
  aWs2811[0].sendLedData();
  ++nNumFrame;
  delay( 50 );  

}

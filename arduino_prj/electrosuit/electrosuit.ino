#include <EEPROM.h>

/*
 * La combinaison d'Electro de Samy
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
int nBackGroundSequence = 0;
int nBackGroundSequenceInc = 1;
void loop()
{
  if( nNumFrame >= 12 ) // the 11 will light off
  {
    nNumFrame = 0;
    ++nNumSequence;
    if( (nNumSequence % 2 == 1) )
    {
      delay( 400 );
    }
  }
  
  nBackGroundSequence += nBackGroundSequenceInc;
  if( nBackGroundSequence > 40 )
  {
    nBackGroundSequenceInc = -2;
  }
  else if( nBackGroundSequence < 4 )
  {
    nBackGroundSequenceInc = 2;
    //delay( 400 );
  }
  
  Serial.println( nBackGroundSequence, DEC );
  
  
  uint8_t r, g, b;
  uint8_t rLow = 4, gLow = 20, bLow = 4;
  
  //rLow = nBackGroundSequence; gLow = nBackGroundSequence*1.5; bLow = nBackGroundSequence;
  
  //r = g = b = 255;
  //hueToRGB( (nNumSequence + 255) % 255, &r, &g, &b );
  r = 100; g = 255; b = 100;
  if( 0 )
  {
    // flash!
    aWs2811[0].setColor( 255,255,255 );
  }
  else
  {
    aWs2811[0].setOneBrightOtherLow( 8, 0, nNumFrame-1, r, g, b, rLow, gLow, bLow );
    aWs2811[0].setOneBrightOtherLow( 10, 8, 10-nNumFrame, r, g, b, rLow, gLow, bLow );
    aWs2811[0].setOneBrightOtherLow( 11, 18, nNumFrame, r, g, b, rLow, gLow, bLow );
    aWs2811[0].setOneBrightOtherLow( 10, 29, (10-nNumFrame)-1, r, g, b, rLow, gLow, bLow );
    aWs2811[0].setOneBrightOtherLow( 4, 39, nNumFrame, r, g, b, rLow, gLow, bLow );  
    aWs2811[0].sendLedData();
  }
  ++nNumFrame;
  delay( 30 );  
}

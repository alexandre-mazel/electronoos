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


#include "tags.h"
#include "Ai_WS2811.h"
//#include <../../../../libraries/EEPROM/EEPROM.h> // => generate error when in a .c

const int nNbrReader = 3;
const int nLenCode = 12;

const int nFirstLedPin = 50; // one led per reader
const int nFirstPresencePin = 40; // one pin per reader

#define NUM_PIXELS 16
Ai_WS2811 aWs2811[nNbrReader];
struct CRGB * apLeds[nNbrReader] = {NULL, NULL, NULL};


TagsList * pTagsList = NULL;

int anExtraPin_PrevState[nNbrReader]; // memorize the state of the previous extra pin (one per board)
int anExtraPin_CptEqual[nNbrReader];  // count the number of frame with same value (one per board)
int abExtraPin_BadgeWasHere[nNbrReader]; // was the board present?

int anState[nNbrReader]; // 0: idle, 1: good, 2: bad, 3: memorize, 4: forget

/*
Led phase at ~200fps:
      0: memorize anim
  20000: forget   anim
  40000: good
  50000: bad
  60000: nothing (clear it)
  
*/
unsigned int anCptLedAnim[nNbrReader];

void animate_led()
{
//  return;
  int i;
  for( i = 0; i < nNbrReader; ++i )
  {
    unsigned int val = anCptLedAnim[i];
//    Serial.print( " val: " );
//    Serial.print( val );
    
    if( val > 60000 )
    {
      anCptLedAnim[i] = 60001;
      continue;
    }
    
    // learn anim
    if( val >= 0 && val < 20000 )
    {
      // aWs2811[i].setColor( 0, 255, 255 );      
      if( val <= 100 )
        // aWs2811[i].setVumeter( (val - 0)*10, 0, 1, 1 );
        aWs2811[i].setOnlyOne( (val - 0)*100, 0, 255, 255 );
      else
        anCptLedAnim[i] = 0;
    }    
    else if( val == 19999 )
    {
      anCptLedAnim[i] = 60000;
    } 

    if( val >= 20000 && val < 40000 )
    {
      // aWs2811[i].setColor( 255, 0, 255 );
      if( val <= 20100 )
        aWs2811[i].setOnlyOne( (val - 20000)*100, 255, 0, 255 );
      else
        anCptLedAnim[i] = 20000;
      
    }    
    else if( val == 39999 )
    {
      anCptLedAnim[i] = 60000;
    }

    if( val >= 40000 && val <= 49000 )
    {
      //aWs2811[i].setColor( 0, 255, 0 );
      if( val <= 40100 )
        aWs2811[i].setVumeter( (val - 40000)*100, 0, 1, 0 );
    }    

    if( val == 50000 )
    {
      aWs2811[i].setColor( 255, 0, 0 );
    }    
    
    if( anCptLedAnim[i] == 60000 )
    {
      aWs2811[i].setColor( 0, 0, 0 );      
    }
    
    if( val != 49001 && val != 59001 )
    {
      ++anCptLedAnim[i];
    }
  }
  
//  Serial.println("");
}


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
  Serial1.begin(9600);
  Serial2.begin(9600);
  Serial3.begin(9600);  
  pTagsList = (TagsList*)malloc(sizeof(TagsList)*nNbrReader);
  for( i = 0; i < nNbrReader; ++i )
  {
    TagsList_init( &pTagsList[i] );
    anCptLedAnim[i*2+0] = 60000;
    anCptLedAnim[i*2+1] = 60000;
    anExtraPin_CptEqual[i] = 0;
  }
  // setup pin
  for( i = 0; i < nNbrReader; ++i )
  {
    pinMode( nFirstLedPin+i, OUTPUT );
    pinMode( nFirstPresencePin+i, INPUT );
  }

  for( i = 0; i < nNbrReader; ++i )
  {
    aWs2811[i].init(nFirstLedPin+i,NUM_PIXELS);
    apLeds[i] = (struct CRGB*)aWs2811[i].getRGBData();
    aWs2811[i].setDim( 1 );
  }
  aWs2811[0].reducePixelNumber( 5 );  
  aWs2811[1].reducePixelNumber( 5 );
  aWs2811[2].reducePixelNumber( 1 );  
  
  
  check_leds();

  
  Serial.println( "\nArduino started: Table des Aromes v0.9\n" );
  load_eeprom(pTagsList, nNbrReader);
}

int check_code( const char * buf, int nReaderIdx )
{
   /* 
   is the code the good one for this id ?
   return 0/1/2, memorized/good/bad
   */
/*   
   if( pTagsList[nReaderIdx].nNbrTags == 0 )
   {
     Serial.println( "\nMemorising this code for this reader\n" );
     TagsList_addToList( &(pTagsList[nReaderIdx]), buf );
     return 0;
   }
*/   
   if( TagsList_isInList( &(pTagsList[nReaderIdx]), buf ) != -1 )
   {
     return 1;
   }
   return 2;
}

void memorize_code( const char * buf, int nReaderIdx, int bForget )
{
  if( not bForget )
    TagsList_addToList( &(pTagsList[nReaderIdx]), buf );
  else
    TagsList_removeFromList( &(pTagsList[nReaderIdx]), buf );  
}






int analyse_code( const char * buf, int *pnBufLen, int nReaderIdx )
{
  /*
  Analyse a buffer.
  Return:
    -1: if nothing found
    0: if something found (state updated)
  */
  // TODO: check buffer jamais plus grand que nLenCode+2
  int nBufLen = *pnBufLen;
  if( buf[nBufLen-1] != 0x3 )
  {
    // Serial.println( "no code yet" );
    return -1;
  }
   abExtraPin_BadgeWasHere[nReaderIdx] = true;


  if( 0 )
  {
    // print debug
    int i;
    Serial.write( "On " );
    Serial.print( nReaderIdx, DEC);
    Serial.write( ", Code: " );  
    for( i = 0; i < nBufLen; ++i)
    {
      Serial.print( buf[i], DEC );
    }
    Serial.write( " 0x" );
    for( i = 1; i < nBufLen-1; ++i) // first in 2 and last is 3 => jump it!
    {
      Serial.print( buf[i], HEX );
      Serial.write( " " );
    }
  }
  
  *pnBufLen = 0;  
  int nRetCode = TagsList_isMagic( &buf[1] );
  if( nRetCode != 0 )
  {
    anState[nReaderIdx] = nRetCode+2; // 3 or 4
    anCptLedAnim[nReaderIdx] = (nRetCode-1)*20000;
    return 0;
  }
  
  if( anState[nReaderIdx] >= 3 )
  {
    memorize_code( &buf[1], nReaderIdx, anState[nReaderIdx] == 4 );
    anState[nReaderIdx] = 0;
    anCptLedAnim[nReaderIdx] = 60000;
    save_eeprom( pTagsList, nNbrReader );
    return 0;
  }
  
  
  nRetCode = check_code( &buf[1], nReaderIdx );

  if( 0 )
  {
    Serial.write( "\nanalyse_code: retcode: " );
    Serial.print( nRetCode, DEC );
    Serial.write( "\n" );
  }

  if( anState[nReaderIdx] != nRetCode ) // evite de relancer l'animation quand elle est deja en cours (genre mauvais contact sur une anim verte)
  {
    anState[nReaderIdx] = nRetCode;
    anCptLedAnim[nReaderIdx] = (nRetCode)*10000+30000;
  }
  
  return 0;
}


const int nMaxSizeBuf = (nLenCode+2)*2; // ok just nLenCode+2 is enough, but ...
char buf1[nMaxSizeBuf]; int nCpt1 = 0;
char buf2[nMaxSizeBuf]; int nCpt2 = 0;
char buf3[nMaxSizeBuf]; int nCpt3 = 0;

int nFpsCpt = 0;
unsigned long timeFpsBegin = 0;

void loop()
{
  int i;
  if(Serial1.available())
  {
    while(Serial1.available())
    {
      buf1[nCpt1] = Serial1.read();
      ++nCpt1;
    }
    analyse_code( buf1, &nCpt1, 0 );
  }
  if(Serial2.available())
  {
    while(Serial2.available())
    {
      buf2[nCpt2] = Serial2.read();
      ++nCpt2;
    }
    analyse_code( buf2, &nCpt2, 1 );
  }  
  if(Serial3.available())
  {
    while(Serial3.available())
    {
      //Serial.write(Serial3.read());
      buf3[nCpt3] = Serial3.read();
      ++nCpt3;      
    }
    analyse_code( buf3, &nCpt3, 2 );
  }
 
  
  for( i = 0; i < nNbrReader; ++i )
  {
    int nVal = digitalRead(nFirstPresencePin+i);
    if( nVal == anExtraPin_PrevState[i] )
    {
      ++anExtraPin_CptEqual[i];

      if( abExtraPin_BadgeWasHere[i] && anExtraPin_CptEqual[i] > 11 ) // was > 16 (ok when you're at >~90fps...) // the crucial point is it depends of the fps...
      //if( anExtraPin_CptEqual[1] > 16 )
      {
        // tag disappear, turn off led right now!
        Serial.print( "BADGE disappear: " );
        Serial.println( i );
        abExtraPin_BadgeWasHere[i] = false;
        if( anState[i] < 3 )
        {
          anState[i] = 0;
          anCptLedAnim[i] = 60000;
        }
      }   
    }
    else
    {
      if( 0 )
      {
        Serial.print( "reader: ");
        Serial.print( i );
        Serial.print( ", change after same val: ");
        Serial.print( nVal );      
        Serial.print(", cpt: ");
        Serial.print( anExtraPin_CptEqual[i] );
        Serial.print(", was here: ");
        Serial.print( abExtraPin_BadgeWasHere[i] );
        Serial.println("");
      }
      
      anExtraPin_PrevState[i] = nVal;
      anExtraPin_CptEqual[i] = 0;
    }
  }

  animate_led();
  delay(10);

  
  ++nFpsCpt;
  const int nNbrFrameToCompute = 300*1;
  if( nFpsCpt == nNbrFrameToCompute )
  {
    unsigned long nNow = micros();
    unsigned long nDuration = nNow - timeFpsBegin;
    
    Serial.print( "frame: " );
    Serial.print( nDuration/nNbrFrameToCompute );
    Serial.print( "us, fps: " );
    Serial.println( 1000000.*nNbrFrameToCompute/nDuration );
    timeFpsBegin = nNow;
    nFpsCpt = 0;
    
    // a simple analog read is running at 5413fps (184us per frame)
  }  
}

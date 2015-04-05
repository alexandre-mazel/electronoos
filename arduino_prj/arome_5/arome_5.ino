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
int abExtraPin_BoardWasHere[nNbrReader]; // was the board present?

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
  int i;
  for( i = 0; i < nNbrReader; ++i )
  {
    unsigned int val = anCptLedAnim[i];
    if( val > 60000 )
    {
      anCptLedAnim[i] = 60000;
      break;
    }
    
    // learn anim
    if( val == 0 )
    {
      aWs2811[i].setColor( 255, 0, 255 );
    }    
    else if( val == 19999 )
    {
      anCptLedAnim[i] = 60000;
    } 

    if( val == 20000 )
    {
      aWs2811[i].setColor( 0, 255, 255 );
    }    
    else if( val == 39999 )
    {
      anCptLedAnim[i] = 60000;
    }

    if( val == 40000 )
    {
      aWs2811[i].setColor( 0, 0, 255 );
      --anCptLedAnim[i]; // stuck it!
    }    

    if( val == 50000 )
    {
      aWs2811[i].setColor( 255, 0, 0 );
      --anCptLedAnim[i]; // stuck it!
    }    
    
    if( anCptLedAnim[i] == 60000 )
    {
      aWs2811[i].setColor( 0, 0, 0 );      
    }
    ++anCptLedAnim[i];
  }
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
    aWs2811[i].setColor( 255, 0, 255 );    
  }
  delay( 1000 );  
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
  }
  aWs2811[1].m_nLeds = 12;
  
  
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
   abExtraPin_BoardWasHere[nReaderIdx] = true;
   if( TagsList_isInList( &(pTagsList[nReaderIdx]), buf ) != -1 )
   {
     return 1;
   }
   return 2;
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
    return -1;
  }
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
    memorize_code( &buf[1], anState[nReaderIdx] == 4 );
    return 0;
  }
  
  
  nRetCode = check_code( &buf[1], nReaderIdx );

  Serial.write( "\nretcode: " );
  Serial.print( nRetCode, DEC );
  Serial.write( "\n" );

  anState[nReaderIdx] = nRetCode;
  anCptLedAnim[nReaderIdx] = (nRetCode)*10000+40000;
  
  return 0;
}


const int nMaxSizeBuf = (nLenCode+2)*2; // ok just nLenCode+2 is enough, but ...
char buf1[nMaxSizeBuf]; int nCpt1 = 0;
char buf2[nMaxSizeBuf]; int nCpt2 = 0;
char buf3[nMaxSizeBuf]; int nCpt3 = 0;

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
 
  animate_led();
  // delay(0);
  
  for( i = 0; i < nNbrReader; ++i )
  {
    int nVal = digitalRead(nFirstPresencePin+i);
    if( nVal == anExtraPin_PrevState[i] )
    {
      ++anExtraPin_CptEqual[i];
      if( abExtraPin_BoardWasHere[i] && anExtraPin_CptEqual[i] > 16 )
      //if( anExtraPin_CptEqual[1] > 16 )
      {
        // tag disappear, turn off led right now!
        Serial.println( "led disappear!" );
        abExtraPin_BoardWasHere[i] = false;
        anCptLedAnim[i] = 60000;

      }   
    }
    else
    {
      anExtraPin_PrevState[i] = nVal;
      anExtraPin_CptEqual[i] = 0;
    }
  }
}

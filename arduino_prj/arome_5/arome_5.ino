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

const int nFirstLedPin = 22; // one led per reader
const int nFirstPresencePin = 48; // one pin per reader

#define NUM_PIXELS 8
Ai_WS2811 aWs2811[nNbrReader];
struct CRGB * apLeds[nNbrReader] = {NULL, NULL, NULL};


TagsList * pTagsList = NULL;

int anExtraPin_PrevState[nNbrReader]; // memorize the state of the previous extra pin (one per board)
int anExtraPin_CptEqual[nNbrReader];  // count the number of frame with same value (one per board)
int abExtraPin_BoardWasHere[nNbrReader]; // was the board present?

/*
Led phase at ~200fps:
*/
unsigned int anCptLedAnim[nNbrReader];

void animate_led()
{
  int i;
  for( i = 0; i < nNbrReader*2; ++i )
  {
    unsigned int val = anCptLedAnim[i];
    if( val > 60000 )
    {
      anCptLedAnim[i] = 60000;
    }
    
    // learn anim
    else if( val == 0 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
    }    
    else if( val == 500 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
    }    
    else if( val == 1000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
    }    
    else if( val == 2000 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
    }    
    else if( val == 3000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
    }    
    else if( val == 4000 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
      anCptLedAnim[i] = 60000;
    }    

    // good anim
    else if( val == 5000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
    }
    else if( val == 6000 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
    }
    else if( val == 7000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
      anCptLedAnim[i] = 45000;
      if(i==2)
        anCptLedAnim[i] = 60000; // temp test alternate patched
    }

    // bad anim
    else if( val == 10000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
    }
    else if( val == 11000 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
    }
    else if( val == 12000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
    }    
    else if( val == 13000 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
    }
    else if( val == 14000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
    }    
    else if( val == 15000 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
    }
    else if( val == 16000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
    }    
    else if( val == 17000 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
    }
    else if( val == 18000 )
    {
      digitalWrite(nFirstLedPin+i, HIGH);
      anCptLedAnim[i] = 45000;
      if(i==3)
        anCptLedAnim[i] = 60000; // temp test alternate patched
      
    }

    else if( val >= 30000 && val < 59000)
    {
      int nPinDown = (59000 - val)/(590-300); // will go from 100 to 0
      nPinDown = (nPinDown*63)/100;
      if( nPinDown == 0 )
        nPinDown = 1;
      //Serial.println( nPinDown, DEC );
      if( (val & 63) == 0 )
        digitalWrite(nFirstLedPin+i, HIGH);
      else if( (val & 63) == nPinDown || (val & 63) == nPinDown+1 ) // si depuis la frame d'avant, pindown est baissé de un et qu'on etait juste sur la frame avant l'extinction, on peut la rater, d'ou le deuxieme test.
        digitalWrite(nFirstLedPin+i, LOW);
    }

    else if( val == 59000 )
    {
      digitalWrite(nFirstLedPin+i, LOW);
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
    aWs2811[i].setColor( 255,0, 0 );
  }
  delay( 2000 );
  for( i = 0; i < nNbrReader; ++i )
  {
    aWs2811[i].setColor( 255, 0, 255 );    
  }
  delay( 1000 );  
}

/*
const byte nEepromVersion = 1;

void load_eeprom2(TagsList * pTagsList, int nNbrReader)
{
  byte nEepromCurrent = EEPROM.read( 0 );
  Serial.print( "eeprom current version: " );
  Serial.println( nEepromCurrent );
  if( nEepromVersion != nEepromCurrent )
  {
    return;
  }
  Serial.println( "Loading eeprom..." );
  int nOffset = 1;
  for( int i = 0; i < nNbrReader; ++i )
  {
    nOffset += TagsList_readFromEprom( &pTagsList[i], nOffset );
  }  
}

void save_eeprom2(TagsList * pTagsList, int nNbrReader)
{
  Serial.println( "Saving eeprom..." );
  EEPROM.write( 0, nEepromVersion );
  int nOffset = 1;
  for( int i = 0; i < nNbrReader; ++i )
  {
    nOffset += TagsList_writeToEprom( &pTagsList[i], nOffset );
  }  
}
*/

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
  
  
  check_leds();

  
  Serial.println( "\nArduino started: Table des Aromes v0.9\n" );
  load_eeprom(pTagsList, nNbrReader);
}

int check_code( const char * buf, int nReaderIdx )
{
   /* 
   is the code the good one for this id ?
   return 0/1/2, cf analyse_code for meanings
   */
   if( pTagsList[nReaderIdx].nNbrTags == 0 )
   {
     Serial.println( "\nMemorising this code for this reader\n" );
     TagsList_addToList( &(pTagsList[nReaderIdx]), buf );
     return 0;
   }
   abExtraPin_BoardWasHere[nReaderIdx] = true;
   if( TagsList_isInList( &(pTagsList[nReaderIdx]), buf ) )
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
    -1: if nothing found, 0
    +0: code memorised
    +1: good id
    +2: if bad id
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
  int nRetCode = TagsList_isMagic( &buf[1] );  
  
  
   nRetCode = check_code( &buf[1], nReaderIdx );
  *pnBufLen = 0;

  Serial.write( "\nretcode: " );
  Serial.print( nRetCode, DEC );
  Serial.write( "\n" );

  if( nRetCode == 0 )
  {
    anCptLedAnim[nReaderIdx*2+0] = 0;
    anCptLedAnim[nReaderIdx*2+1] = 0;
  }
  else if( nRetCode == 1 )
  {
    anCptLedAnim[nReaderIdx*2+0] = 5000;
    anCptLedAnim[nReaderIdx*2+1] = 59000;
  }
  else
  {
    anCptLedAnim[nReaderIdx*2+1] = 10000;
    anCptLedAnim[nReaderIdx*2+0] = 59000;    
  }
  
  return nRetCode;
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
      }   
    }
    else
    {
      anExtraPin_PrevState[i] = nVal;
      anExtraPin_CptEqual[i] = 0;
    }
  }
}

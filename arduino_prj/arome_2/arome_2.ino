/*
 * La table des Aromes des Caves du Louvre
 * 
 * Version number: cf the message in the print of the setup function
 * Author: Alexandre Mazel
 * copyright (c) A.Mazel 2015
 */

#include <avr/pgmspace.h>
const char pad[3] PROGMEM = { 0 };

const int nNbrReader = 3;
const int nLenCode = 12;

const int nFirstLedPin = 28; // first is green, second is red

char aaMemorised[nNbrReader][nLenCode];

/*

Led phase at ~200fps:
    0: learn first frame
 5000: good first frame
10000: bad first frame
30000: slow turn off
59000: turn off
60000: nothing
*/
unsigned int anCptLedAnim[nNbrReader*2];

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
    }

    else if( val >= 30000 && val < 59000)
    {
      int nPinDown = (59000 - val)/(590-300); // will go from 100 to 0
      if( nPinDown == 0 )
        nPinDown = 1;
      //Serial.println( nPinDown, DEC );
      if( (val % 100) == 0 )
        digitalWrite(nFirstLedPin+i, HIGH);
      else if( (val % 100) == nPinDown || (val % 100) == nPinDown+1 ) // si depuis la frame d'avant, pindown est baissé de un et qu'on etait juste sur la frame avant l'extinction, on peut la rater, d'ou le deuxieme test.
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
  int i;
  for( i = 0; i < nNbrReader; ++i )
  {
    digitalWrite(nFirstLedPin+i*2+0, HIGH);
    digitalWrite(nFirstLedPin+i*2+1, HIGH);
  }
  delay( 2000 );
  for( i = 0; i < nNbrReader; ++i )
  {
    digitalWrite(nFirstLedPin+i*2+0, LOW);
    digitalWrite(nFirstLedPin+i*2+1, LOW);
  }
  delay( 1000 );  
}
void setup()
{
  pad[0];
  int i;
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(9600);
  Serial3.begin(9600);  
  for( i = 0; i < nNbrReader; ++i )
  {
    aaMemorised[i][0] = 0;
    anCptLedAnim[i*2+0] = 60000;
    anCptLedAnim[i*2+1] = 60000;    
  }
  // setup pin
  for( i = 0; i < nNbrReader; ++i )
  {
    pinMode(nFirstLedPin+i*2+0, OUTPUT);
    pinMode(nFirstLedPin+i*2+1, OUTPUT);  
  }
  check_leds();
  
  Serial.println( "\nArduino started: Table des Aromes v0.7\n" );
}

int check_code( const char * buf, int nReaderIdx )
{
 /* 
   is the code the good one for this id ?
   return 0/1/2, cf analyse_code for meanings
 */
 if( aaMemorised[nReaderIdx][0] == 0 )
 {
   Serial.println( "\nMemorising this code for this reader\n" );
   for( int i = 0; i < nLenCode; ++i )   
   {
     aaMemorised[nReaderIdx][i] = buf[i]; // memcpy ?
   }
   return 0;
 }
   for( int i = 0; i < nLenCode; ++i )   
   {
     if( aaMemorised[nReaderIdx][i] != buf[i] ) // memcmp ?
     {
       return 2;
     }
   }   
   return 1;
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
  int nRetCode = check_code( &buf[1], nReaderIdx );
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
}

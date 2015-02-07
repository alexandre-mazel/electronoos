/*
 * La table des Aromes des Caves du Louvre
 * 
 * Version number: cf the message in the print of the setup function
 * Author: Alexandre Mazel
 * copyright (c) A.Mazel 2015
 */
 
const int nNbrReader = 3;
const int nLenCode = 12;

const int nFirstLedPin = 28;
char aaMemorised[nNbrReader][nLenCode];

void check_leds( void )
{
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
  int i;
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(9600);
  Serial3.begin(9600);  
  for( i = 0; i < nNbrReader; ++i )
  {
    aaMemorised[i][0] = 0;
  }
  // setup pin
  for( i = 0; i < nNbrReader; ++i )
  {
    pinMode(nFirstLedPin+i*2+0, OUTPUT);
    pinMode(nFirstLedPin+i*2+1, OUTPUT);  
  }
  check_leds();
  
  Serial.println( "\narduino started: v0.6\n" );
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
    for( i = 0; i < 10; ++i )
    {
      digitalWrite(nFirstLedPin+nReaderIdx*2, HIGH);
      delay(100);
      digitalWrite(nFirstLedPin+nReaderIdx*2, LOW);
      delay(50);
    }
  }
  else
  {
    digitalWrite(nFirstLedPin+nReaderIdx*2+(nRetCode-1+1)%2, LOW);
    digitalWrite(nFirstLedPin+nReaderIdx*2+(nRetCode-1)%2, HIGH);  
  }
  
  
  return nRetCode;
}

const int nMaxSizeBuf = (nLenCode+2)*3; // ok just nLenCode+2 is enough, but ...
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
 
  for( i = 0; i < nNbrReader; ++i )
  {
    //digitalWrite(30+i*2+0, HIGH);
    //digitalWrite(30+i*2+1, HIGH);
  }
 
}

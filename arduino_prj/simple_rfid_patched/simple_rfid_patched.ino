/*
 * Simple Rfid reader - patched to have the disappear badge signal
 * 
 * Author: Alexandre Mazel
 * copyright (c) A.Mazel 2015
 */

const int nFirstLedPin = 28; // first is green, second is red
const int nExtraPin = 40;

int nExtraPin_CptEqual;
int bExtraPin_BoardWasHere;
int nExtraPin_PrevState;

const int nLenCode = 12;
const int nMaxSizeBuf = (nLenCode+2)*2; // ok just nLenCode+2 is enough, but ...
char buf1[nMaxSizeBuf]; int nCpt1 = 0;

void setup()
{
  Serial.begin(9600); // for debug
  Serial2.begin(9600); // for reading the rfid

  nExtraPin_CptEqual = 0;
  pinMode(nFirstLedPin, OUTPUT);
  pinMode(nExtraPin, INPUT);  
  
  Serial.println( "\nArduino started: Simple RFID reader - patched\n" );
}

void loop()
{
  if(Serial2.available())
  {
    while(Serial2.available())
    {
      buf1[nCpt1] = Serial2.read();
      ++nCpt1;
      Serial.print( buf1 );      
    }
    Serial.println( "\n" );
    digitalWrite(nFirstLedPin, HIGH);    
    bExtraPin_BoardWasHere = true;
  }
 
  int nVal = digitalRead(nExtraPin);
  if( nVal == nExtraPin_PrevState )
  {
    ++nExtraPin_CptEqual;
    if( bExtraPin_BoardWasHere && nExtraPin_CptEqual > 16 ) // state are more stable when no badge
    {
      // tag disappear, turn off led right now!
      digitalWrite(nFirstLedPin, LOW);
      Serial.println( "badge disappear!" );
      bExtraPin_BoardWasHere = false;
    }   
  }
  else
  {
    nExtraPin_PrevState = nVal;
    nExtraPin_CptEqual = 0;
  }
  
  delay(0);
 
}

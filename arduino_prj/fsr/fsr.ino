#include "Ai_WS2811.h"

#define SENSOR_PIN 0

#define NUM_PIXELS 16
#define DATA_PIN 53
#define SPEAKER_PIN 11

struct CRGB *leds;
Ai_WS2811 ws2811;

void setVumeter( int nValue )
{
  // light the vumeter
  // -nValue: [0..10000]
  const int nNbrValuePerLed = 10000/NUM_PIXELS;
  int nNbrLedToLighten = nValue / nNbrValuePerLed;
  int nNbrRemaining = nValue - (nNbrLedToLighten * nNbrValuePerLed);
//  Serial.print( "nNbrValuePerLed: " );
//  Serial.print( nNbrValuePerLed, DEC );
//  Serial.print( "nNbrLedToLighten: " );
//  Serial.print( nNbrLedToLighten, DEC );
//  Serial.print( "nNbrRemaining: " );
//  Serial.println( nNbrRemaining, DEC );
  
  nNbrRemaining = map( nNbrRemaining, 0, nNbrValuePerLed, 0, 255 );
  int i;
  for( i = 0; i < nNbrLedToLighten; ++i )
  {
    leds[i].r = 255;
    leds[i].g = 255;
    leds[i].b = 255;    
  }
  if( i < NUM_PIXELS )
  {
    leds[i].r = nNbrRemaining;
    leds[i].g = nNbrRemaining;
    leds[i].b = nNbrRemaining;
    ++i;
  }
  for(; i < NUM_PIXELS; ++i )
  {
    leds[i].r = 0;
    leds[i].g = 0;
    leds[i].b = 0;    
  }
  ws2811.dim(8);
  ws2811.sendLedData();
}

//some initial values
void setup()
{
  Serial.begin(9600);
  ws2811.init(DATA_PIN,NUM_PIXELS);
  leds = (struct CRGB*)ws2811.getRGBData();
    
}

void playTone(int tone, int duration) {
  for (long i = 0; i < duration * 1000L; i += tone * 2) {
    digitalWrite(SPEAKER_PIN, HIGH);
    delayMicroseconds(tone);
    digitalWrite(SPEAKER_PIN, LOW);
    delayMicroseconds(tone);
  }
}

void playNote(char note, int duration) {
  char names[] = { 'c', 'd', 'e', 'f', 'g', 'a', 'b', 'C' };
  int tones[] = { 1915, 1700, 1519, 1432, 1275, 1136, 1014, 956 };
  
  // play the tone corresponding to the note name
  for (int i = 0; i < 8; i++) {
    if (names[i] == note) {
      playTone(tones[i], duration);
    }
  }
}

int bPushed = 0;
void loop()
{
    int nVal = analogRead(  SENSOR_PIN ); // nLight is big when darker
    if( nVal < 500 )
    {
      setVumeter( (500-nVal)*20 );
      if( !bPushed )
      {
        bPushed = 1;
        playNote( 'c', 200 );
        playNote( 'd', 200 );
        playNote( 'e', 200 );        
      }
    }
    else
    {
      if( bPushed )
      {
        bPushed = 0;
       setVumeter( 0 );
      }
    }
    Serial.println( nVal );
    delay(100);
    
}


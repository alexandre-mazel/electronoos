#include "Ai_WS2811.h"

#define NUM_PIXELS 8
#define DATA_PIN 53

#define PHOTO_PIN 8

Ai_WS2811 ws2811;

struct CRGB {
  unsigned char g;
  unsigned char r;
  unsigned char b;
} *leds;

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
  ws2811.dim(16);
  ws2811.sendLedData();
}

int nFpsCpt = 0;
unsigned long timeFpsBegin;

//some initial values
void setup()
{
  ws2811.init(DATA_PIN,NUM_PIXELS);
  leds = (struct CRGB*)ws2811.getRGBData();
  Serial.begin(9600);
  //setVumeter( 10000 ); // full all led
  //setVumeter( 1250 ); // 1 led full
  setVumeter( 0 ); // 0 led
  timeFpsBegin = micros();
}

int nCpt = 0;
int bPrevLighten = false;
int nCptHidden = 0;
unsigned long timeLast = 0;
int nCptFadeOut = 0;
void loop()
{
  int nLight = analogRead(  PHOTO_PIN ); // nLight is big when darker
  //nLight = map( nLight, 0, 900,10000, 0);
  
  int bLighten;
  if( bPrevLighten ) // hysteresis
    // 520 and 490 are great with 1 only led WS2811, even if running very fast.
    // 250 and 200 are great with the iphone led
    bLighten = nLight < 250; 
  else
     bLighten = nLight < 200; 
     

  //Serial.println( nLight, DEC );  

  if( bPrevLighten != bLighten )
  {
    if( bLighten )
    {
      //Serial.print( "litten: " );      
      //Serial.println( nLight, DEC );
    }
    else
    {
      ++nCptHidden;
      //Serial.println( nCptHidden, DEC );
      const int nNbrBarrePerWheel = 6; // nbr de "rayon"
      const int nNbrWheelToMeasures = 1;
      if( nCptHidden == nNbrWheelToMeasures*nNbrBarrePerWheel )
      {
        unsigned long nNow = micros();
        unsigned long nDuration = nNow - timeLast;
        Serial.print( "nDuration: " );
        Serial.println( nDuration, DEC );        
        float rpmicro = nNbrWheelToMeasures*1000000. / nDuration;
        Serial.print( "rpmicro: " );
        Serial.println( rpmicro );
        timeLast = nNow;
        nCptHidden = 0;
        nCptFadeOut = rpmicro*2000;
      }
    }
    bPrevLighten = bLighten;
  }
  if( nCptFadeOut > -1 )
  {
    setVumeter( nCptFadeOut );
    --nCptFadeOut;
  }
  
  //delay(1);
  
  
  // fps computation
  ++nCpt;
  ++nFpsCpt;
  const int nNbrFrameToCompute = 10000*2;
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

/**
 * HVS to RGB comversion (simplified to the range 0-255)
 **/
void setHue(int h, uint8_t n) {
  //this is the algorithm to convert from RGB to HSV
  double r=0; 
  double g=0; 
  double b=0;

//  double hf=h/42.5; // Not /60 as range is _not_ 0-360

  int i=(int)floor(h/42.5);
  double f = h/42.5 - i;
  double qv = 1 - f;
  double tv = f;

  switch (i)
  {
  case 0: 
    r = 1;
    g = tv;
    break;
  case 1: 
    r = qv;
    g = 1;
    break;
  case 2: 
    g = 1;
    b = tv;
    break;
  case 3: 
    g = qv;
    b = 1;
    break;
  case 4:
    r = tv;
    b = 1;
    break;
  case 5: 
    r = 1;
    b = qv;
    break;
  }

  leds[n].r = constrain((int)255*r,0,255);
  leds[n].g = constrain((int)255*g,0,255);
  leds[n].b = constrain((int)255*b,0,255);
}

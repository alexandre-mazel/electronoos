// Idee: on fait juste un signal pour allumer les 4 leds et on branchera les 3 senteurs en paralelles comme sur Fossilation (voire 6)

#include <FastLED.h> // FastLed Neopixel by David Madison and FastLed 3.9.8

//#define MEGA
#define PRO_MICRO
//#define XIAO_C3


#ifdef MEGA

# pragma message "ATTENTION: On compile pour le MEGA !"

#   define PIN_LEDS 50

#endif // MEGA


#ifdef PRO_MICRO

# pragma message "ATTENTION: On compile pour le PRO_MICRO !"


#   define PIN_LEDS 9    // la 9 c'est la A9

#endif // PRO_MICRO


#define NUM_LEDS 4


CRGB leds[NUM_LEDS];


int32_t hueToRGB( int nHue )
{
  //this is the algorithm to convert from RGB to HSV
  // nHue between 0 and 254
  double r=0; 
  double g=0; 
  double b=0;

  double hf=nHue/42.5; // Not /60 as range is _not_ 0-360

  int i=(int)floor(nHue/42.5);
  double f = nHue/42.5 - i;
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
  
  int32_t ir = constrain((int)255*r,0,255);
  int32_t ig = constrain((int)255*g,0,255);  
  int32_t ib = constrain((int)255*b,0,255);
  return (ir << 16) | (ig << 8) | ib;
}
  
  
void animate_rainbow_mode()
{
  static int static_nHueColor = 0;
  const int nCoefRalentisseur = 16;
   
  int32_t color = hueToRGB( static_nHueColor/nCoefRalentisseur );

  for( int dot = 0; dot < NUM_LEDS; ++dot )
  { 
    leds[dot] = color;
  }
  
  FastLED.show();
  
  ++static_nHueColor;
  if( static_nHueColor >= 255*nCoefRalentisseur )
  {
    static_nHueColor = 0;
  }
  
}



////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
void setup()
{
    Serial.begin(57600);

    Serial.println( "\nArduino started: Table des Aromes - simplified rainbow v0.7\n" );
    
    pinMode( PIN_LEDS, OUTPUT );
    FastLED.addLeds<NEOPIXEL, PIN_LEDS>(leds, NUM_LEDS); 
}


////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////

int nFpsCpt = 0;
unsigned long timeFpsBegin;

void loop()
{
  animate_rainbow_mode();
  delay(10);

  
  ++nFpsCpt;
  const int nNbrFrameToCompute = 300*1;
  if( nFpsCpt == nNbrFrameToCompute && 0 )
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

#include <FastLED.h> // FastLed Neopixel by David Madison and FastLed 3.9.8

#define NUM_LEDS 60 // number of led present in your strip
#define DATA_PIN 53 // digital pin of your arduino

CRGB leds[NUM_LEDS];


uint32_t hueToHexa( int nHue )
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
  
  uint32_t ir = constrain((int)255*r,0,255);
  uint32_t ig = constrain((int)255*g,0,255);  
  uint32_t ib = constrain((int)255*b,0,255);  

  return (ir << 16) | (ig << 8) | ib;
}

void setup() 
{
  Serial.begin(115200);
  // FastLED.addLeds(leds, NUM_LEDS);
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS); 
}

void chaser(int nDelay=500)
{
  // une led qui se balade d'un coté a l'autre
  for(int dot=(NUM_LEDS-1) ; dot >=0 ; dot--)
  {
    leds[dot] = CRGB::Green;
    FastLED.show();
    leds[dot] = CRGB::Black;
    delay(nDelay);
  }

  for(int dot = 0;dot < NUM_LEDS; dot++)
  { 
    leds[dot] = CRGB::Red;
    FastLED.show();
    leds[dot] = CRGB::Black;
    delay(nDelay);
  }
}

void serialGlow(int nDelay=500)
{
  // une led qui se balade d'un coté a l'autre
  for(int dot=(NUM_LEDS-1) ; dot >=0 ; dot--)
  {
    leds[dot] = CRGB::HotPink;
    FastLED.show();
    delay(nDelay);
  }

  for(int dot = 0;dot < NUM_LEDS; dot++)
  { 
    leds[dot] = CRGB::Blue;
    FastLED.show();
    delay(nDelay);
  }
}

void strobo(int nDelay=100)
{
  for(int dot = 0;dot < NUM_LEDS; dot++)
  { 
    leds[dot] = CRGB::White;
  }
  FastLED.show();
  delay(nDelay);

  for(int dot = 0;dot < NUM_LEDS; dot++)
  { 
    leds[dot] = CRGB::Black;
  }
  FastLED.show();
  delay(nDelay*2); // because leds takes more time to turn off
}

void medusa(int nDelay=100)
{
  for( int hue = 0; hue < 255; ++hue )
  {
    uint32_t color = hueToHexa( hue);
    for(int dot = 0; dot < NUM_LEDS; dot++)
    { 
      leds[dot] = color;
    }
    FastLED.show();
    delay(nDelay);
  }
}


void beat(int nBpm)
{
  int nDelay = 1000L*60/(nBpm*2); // delay is half period
  const int nTimeToSend = 2; // depend of the number of led, 2 is great for 2
  for(int dot = 0;dot < NUM_LEDS; dot++)
  { 
    leds[dot] = CRGB::Blue;
  }
  FastLED.show();
  delay(nDelay-nTimeToSend);

  for(int dot = 0;dot < NUM_LEDS; dot++)
  { 
    leds[dot] = CRGB::Black;
  }
  FastLED.show();
  delay(nDelay-nTimeToSend);
}

void loop()
{ 
  for(int i = 10; i < 10; ++i )
  {
    chaser(10);
  }

  for(int i = 10; i < 3; ++i )
  {
    medusa(100);
  }

  for(int i = 10; i < 5; ++i )
  {
    serialGlow(100);
  }

  for(int i = 10000; i < 2000; ++i )
  {
    strobo(20);
  }

  for(int i = 0; i < 32; ++i )
  {
    beat(120);
  }

  static int32_t last = 0;
  Serial.println(millis()-last);
  last = millis();
}
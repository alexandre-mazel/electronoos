#include <FastLED.h> // FastLed Neopixel by David Madison and FastLed 3.9.8

#define NUM_LEDS 5 // number of led present in your strip
#define DATA_PIN 53 // digital pin of your arduino

CRGB leds[NUM_LEDS];


void setup() 
{
  // FastLED.addLeds(leds, NUM_LEDS);
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS); 
}

void loop()
{ 
  for(int dot=(NUM_LEDS-1) ; dot >=0 ; dot--)
  {
    leds[dot] = CRGB::Green;

    FastLED.show();

    leds[dot] = CRGB::Black;

    delay(300);
  }

  for(int dot = 0;dot < NUM_LEDS; dot++)
  { 
    leds[dot] = CRGB::Red;

    FastLED.show();

    leds[dot] = CRGB::Black;

    delay(300);
}

}
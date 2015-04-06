#include "Ai_WS2811.h"

#define NUM_PIXELS 16 // 8 // 12 // 16
#define DATA_PIN 53 // work fine with 53 but not 23! nor 52 ... ??? for 53 you'll need to set led bit a 0, 52: led pit a 1 et 51: led bit a 0 cf http://arduino.cc/en/Hacking/PinMapping2560

Ai_WS2811 ws2811;

struct CRGB *leds;

//some initial values
void setup()
{
  ws2811.init(DATA_PIN,NUM_PIXELS);
  leds = (struct CRGB*)ws2811.getRGBData();
  Serial.begin(9600);
}

int nCpt = 0;
void loop()
{
  for( int i = 0; i < 16; ++i )
  {
    if( i == 15 || i < 7 )
    {
      leds[i].r = 0;
      leds[i].g = 255;
      leds[i].b = 0;
    }
  }
  ws2811.sendLedData();
  delay(1000);
  return;
  
  //Serial.println( nCpt, DEC );
  if( nCpt > 20 )
  {
    rainbow();
//    delay(1);
  }
  else   if( nCpt > 10 )
  {
    for (int j = -1; j < NUM_PIXELS/2; ++j)
    {
      for (int led = 0; led < NUM_PIXELS/2; ++led) 
      {
        leds[NUM_PIXELS/2-1-led].g = 0;
        if( led > j )
          leds[NUM_PIXELS/2-1-led].r = 0;
        else
          leds[NUM_PIXELS/2-1-led].r = 255;        
        leds[NUM_PIXELS/2-1-led].b = 0;      
        
        leds[NUM_PIXELS/2-0+led].g = 0;
        if( led > j )
          leds[NUM_PIXELS/2-0+led].r = 0;
        else
          leds[NUM_PIXELS/2-0+led].r = 255;        
        leds[NUM_PIXELS/2-0+led].b = 0;      
        
      }
      ws2811.sendLedData();
      delay(100);      
    }
      
    for (int j = NUM_PIXELS/2; j >= -1 ; --j)
    {
      for (int led = 0; led < NUM_PIXELS/2; ++led) 
      {
        leds[NUM_PIXELS/2-1-led].g = 0;
        if( led > j )
          leds[NUM_PIXELS/2-1-led].r = 0;
        else
          leds[NUM_PIXELS/2-1-led].r = 255;        
        leds[NUM_PIXELS/2-1-led].b = 0;      
        
        leds[NUM_PIXELS/2-0+led].g = 0;
        if( led > j )
          leds[NUM_PIXELS/2-0+led].r = 0;
        else
          leds[NUM_PIXELS/2-0+led].r = 255;        
        leds[NUM_PIXELS/2-0+led].b = 0;      
        
      }
      ws2811.sendLedData();
      delay(100);      
    }
  }
  else
  {
    for (int j = -1; j < NUM_PIXELS/2; ++j)
    {
      for (int led = 0; led < NUM_PIXELS/2; ++led) 
      {
        leds[NUM_PIXELS/2-1-led].r = 0;
        if( led > j )
          leds[NUM_PIXELS/2-1-led].g = 0;
        else
          leds[NUM_PIXELS/2-1-led].g = 255;        
        leds[NUM_PIXELS/2-1-led].b = 0;      
        
        leds[NUM_PIXELS/2-0+led].r = 0;
        if( led > j )
          leds[NUM_PIXELS/2-0+led].g = 0;
        else
          leds[NUM_PIXELS/2-0+led].g = 255;        
        leds[NUM_PIXELS/2-0+led].b = 0;      
        
      }
      ws2811.sendLedData();
      delay(100);      
    }
      
    for (int j = NUM_PIXELS/2; j >= -1 ; --j)
    {
      for (int led = 0; led < NUM_PIXELS/2; ++led) 
      {
        leds[NUM_PIXELS/2-1-led].r = 0;
        if( led > j )
          leds[NUM_PIXELS/2-1-led].g = 0;
        else
          leds[NUM_PIXELS/2-1-led].g = 255;        
        leds[NUM_PIXELS/2-1-led].b = 0;      
        
        leds[NUM_PIXELS/2-0+led].r = 0;
        if( led > j )
          leds[NUM_PIXELS/2-0+led].g = 0;
        else
          leds[NUM_PIXELS/2-0+led].g = 255;        
        leds[NUM_PIXELS/2-0+led].b = 0;      
        
      }
      ws2811.sendLedData();
      delay(100);      
      
    }
  }
  ++nCpt;
  if( nCpt > 2000 )
  {
   nCpt = 0;
  }
  
}

/**
 * Color climb function
 **/
void rainbow()
{
  for(int i = 255; i >= 0; i--)
  {
    int val = i;
    for (int led = 0; led < NUM_PIXELS; led++) {
        val = (val + 255/NUM_PIXELS) % 255;
        setHue(val, led);
    }
    ws2811.sendLedData();
    delay(4);    
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

  double hf=h/42.5; // Not /60 as range is _not_ 0-360

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

#include <FastLED.h> // FastLed Neopixel by David Madison and FastLed 3.9.8

//#define NUM_LEDS (16*16) // number of led present in your strip
#define NUM_LEDS (16)

//#define DATA_PIN 45 // digital pin of the connected led
//#define DATA_PIN A10
#define DATA_PIN 45

CRGB leds[NUM_LEDS];

void printHexa2( unsigned char u )
{
  // print u with a leading 0 if needed
  if( u < 16 )
  {
    Serial.print("0");
  }
  Serial.print(u,HEX);
}

void printCRGB( CRGB c )
{
  Serial.print("0x");
  printHexa2( c.raw[2] );
  printHexa2( c.raw[1] );
  printHexa2( c.raw[0] );
}
void printCRGBln( CRGB c )
{
  printCRGB( c );
  Serial.println("");
}


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
  pinMode( DATA_PIN, OUTPUT );
  // FastLED.addLeds(leds, NUM_LEDS);
  FastLED.addLeds<NEOPIXEL, DATA_PIN>(leds, NUM_LEDS); 
}

void chaser(int nDelay=500)
{
  Serial.println( "leds: chaser");

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
  Serial.println( "leds: serialGlow");

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
  Serial.println("Medusa");
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

void full_on()
{
  Serial.println( "leds: full_on");
  for( int dot = 0; dot < NUM_LEDS; ++dot )
  { 
    leds[dot] = CRGB::White;
  }
  FastLED.show();
}

void full_one_color( struct CRGB one_color)
{
  //one_color.raw[0] = 0;
  //one_color.raw[1] = 0;
  //one_color.raw[2] = 0xFF;
  Serial.print( "leds: full_one_color: ");
  printCRGBln( one_color );
  for( int dot = 0; dot < NUM_LEDS; ++dot )
  { 
    leds[dot] = one_color;
  }
  FastLED.show();
}

void erase_all()
{
  memset(leds,0,NUM_LEDS*3);
}

// Cœur 16x16 - chaque pixel codé en RGB (3 octets)
unsigned char heart[16][16][3] = {
    // Ligne 0
    {{0,0,0},{0,0,0},{0,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0},
     {0,0,0},{0,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 1
    {{0,0,0},{0,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},
     {0,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 2
    {{0,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},
     {255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0}},
    // Ligne 3
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},
     {255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0}},
    // Ligne 4
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},
     {255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0}},
    // Ligne 5
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},
     {255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0}},
    // Ligne 6
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},
     {255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 7
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},
     {255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 8
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},
     {255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 9
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},
     {255,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 10
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},
     {0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 11
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},
     {0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 12
    {{255,0,0},{255,0,0},{255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0},
     {0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 13
    {{255,0,0},{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},
     {0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 14
    {{255,0,0},{255,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},
     {0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
    // Ligne 15
    {{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},
     {0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0},{0,0,0}},
     // badly centered
};

/*
unsigned char mario_body_bitmap[16][16][3] = {
    {{255,255,255}, {255,255,255}, {255,246,247}, {255,246,247}, {253,0,9}, {252,0,9}, {245,3,9}, {247,2,9}, {247,2,9}, {250,1,5}, {246,2,7}, {254,254,254}, {255,255,255}, {255,255,255}, {255,255,255}, {254,254,254}},
    {{255,255,255}, {247,255,248}, {248,2,5}, {248,2,5}, {251,2,0}, {250,4,3}, {249,4,4}, {251,2,0}, {251,2,0}, {244,5,1}, {246,2,7}, {243,4,6}, {234,10,5}, {234,10,5}, {253,0,7}, {254,254,254}},
    {{255,255,255}, {250,255,251}, {139,78,4}, {139,78,4}, {151,73,2}, {147,76,0}, {240,198,138}, {245,195,140}, {245,195,140}, {247,193,150}, {6,4,0}, {251,192,146}, {255,251,244}, {255,251,244}, {250,253,243}, {254,254,254}},
    {{254,255,255}, {151,71,7}, {253,191,139}, {253,191,139}, {159,69,4}, {252,192,140}, {251,192,142}, {253,191,142}, {253,191,142}, {246,194,148}, {2,1,1}, {247,193,145}, {249,191,148}, {249,191,148}, {249,194,149}, {255,255,255}},
    {{245,255,255}, {154,71,3}, {254,191,141}, {254,191,141}, {151,72,4}, {152,72,0}, {252,192,143}, {253,191,143}, {253,191,143}, {250,193,141}, {247,192,152}, {6,1,1}, {252,193,142}, {252,193,142}, {253,192,147}, {248,193,146}},
    {{246,255,255}, {152,71,5}, {155,70,1}, {155,70,1}, {250,194,140}, {252,193,134}, {251,192,142}, {253,191,141}, {253,191,141}, {253,191,145}, {8,0,0}, {0,0,0}, {4,0,2}, {4,0,2}, {4,1,1}, {252,255,248}},
    {{254,248,253}, {254,254,251}, {253,254,248}, {253,254,248}, {250,192,144}, {251,192,143}, {249,193,142}, {251,192,142}, {251,192,142}, {248,195,138}, {252,191,139}, {250,191,141}, {252,192,146}, {252,192,146}, {254,254,254}, {254,254,254}},
    {{255,255,255}, {254,255,247}, {229,13,0}, {229,13,0}, {249,2,7}, {0,118,196}, {251,3,5}, {248,3,1}, {248,3,1}, {251,1,2}, {249,1,7}, {255,254,248}, {252,253,251}, {252,253,251}, {255,255,255}, {255,255,255}},
    {{233,255,247}, {239,8,2}, {247,3,0}, {247,3,0}, {241,7,1}, {1,115,202}, {250,1,3}, {240,5,9}, {240,5,9}, {0,119,197}, {246,6,5}, {234,11,0}, {250,3,2}, {250,3,2}, {253,254,254}, {252,252,252}},
    {{249,3,0}, {247,5,0}, {242,9,0}, {242,9,0}, {246,8,0}, {2,112,198}, {7,110,194}, {0,114,200}, {0,114,200}, {2,114,203}, {249,3,0}, {252,0,2}, {249,1,8}, {249,1,8}, {240,5,1}, {254,253,254}},
    {{251,194,138}, {247,196,141}, {248,2,4}, {248,2,4}, {2,109,210}, {255,251,0}, {6,110,183}, {5,110,186}, {5,110,186}, {253,254,1}, {1,113,201}, {252,1,4}, {248,195,144}, {248,195,144}, {251,194,144}, {254,254,254}},
    {{250,193,139}, {252,190,149}, {248,192,143}, {248,192,143}, {2,116,187}, {8,109,185}, {7,111,181}, {8,109,191}, {8,109,191}, {7,110,195}, {4,110,205}, {251,192,139}, {251,192,141}, {251,192,141}, {250,194,145}, {254,254,254}},
    {{253,193,141}, {246,193,151}, {1,115,197}, {1,115,197}, {2,111,195}, {0,115,196}, {0,114,198}, {3,111,189}, {3,111,189}, {0,114,196}, {4,113,191}, {0,116,199}, {254,194,141}, {254,194,141}, {253,193,142}, {255,255,255}},
    {{255,255,248}, {247,254,255}, {1,114,195}, {1,114,195}, {2,113,194}, {15,107,180}, {255,255,255}, {253,252,245}, {253,252,245}, {0,115,199}, {7,112,187}, {8,111,183}, {255,255,255}, {255,255,255}, {255,255,255}, {255,255,255}},
    {{253,255,240}, {157,70,3}, {153,71,6}, {153,71,6}, {151,71,6}, {255,255,255}, {255,255,255}, {255,255,255}, {255,255,255}, {251,254,255}, {151,71,7}, {150,72,8}, {148,74,5}, {148,74,5}, {251,254,253}, {254,254,254}},
    {{151,71,8}, {150,72,10}, {151,71,11}, {151,71,11}, {145,73,18}, {255,255,255}, {255,255,255}, {255,255,255}, {255,255,255}, {254,255,255}, {148,72,12}, {148,72,13}, {150,71,18}, {150,71,18}, {146,72,9}, {254,254,254}},
};
*/

// python C:\Users\alexa\dev\git\electronoos\generate_img\generate_img.py "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_head.png" "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_body.png"
// copy \tmp\imgs.* C:\Users\alexa\dev\git\electronoos\arduino_prj\test_fastled\ /Y
// ou avec walk:
// python C:\Users\alexa\dev\git\electronoos\generate_img\generate_img.py "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_head.png" "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_body_walk_0.png" "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_body_walk_1.png" "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_body_walk_2.png" "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_body_walk_3.png" "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_body_2_walk_0.png" "C:\Users\alexa\dev\git\electronoos\data\bitmap_mario_body_2_walk_1.png"


void drawbitmap16x16(unsigned char bitmap[16][16][3])
{
 Serial.println( "leds: drawbitmap16x16");
  for(int j = 0;j < 16; ++j)
  {
    for(int i = 0;i < 16; ++i)
    { 
      CRGB color = CRGB( ((unsigned long int)(bitmap[j][i][0])<<16) + ((unsigned int)(bitmap[j][i][1])<<8) + bitmap[j][i][2]);
      if(1)
      {
        // dim it
        int dimmer_coef = 4;
        color = CRGB( ((unsigned long int)(bitmap[j][i][0]/dimmer_coef)<<16) + ((unsigned int)(bitmap[j][i][1]/dimmer_coef)<<8) + bitmap[j][i][2]/dimmer_coef);
      }
      if(1)
      {
        // don't draw white
        if( bitmap[j][i][0]>250 && bitmap[j][i][1]>250 && bitmap[j][i][2]>250 )
        {
          continue;
        }
      }
      // une ligne sur 2 est inversée
      if((j%2)==0)
        leds[i+j*16] = color;
      else
        leds[(15-i)+j*16] = color;
    }
  }
  FastLED.show();
}

#include "imgs.h"
void drawImgs(unsigned char * data, int w, int h, int bDontDrawWhite = 0, int dimmer_coef = 1)
{
 Serial.println( "leds: drawImgs");
  for(int j = 0;j < h; ++j)
  {
    for(int i = 0;i < w; ++i)
    { 
      CRGB color = CRGB( ((unsigned long int)(data[(j*w+i)*3+2])<<16) + ((unsigned int)(data[(j*w+i)*3+1])<<8) + data[(j*w+i)*3+0]);
      if(dimmer_coef>1)
      {
        // dim it
        color = CRGB( ((unsigned long int)(data[(j*w+i)*3+2]/dimmer_coef)<<16) + ((unsigned int)(data[(j*w+i)*3+1]/dimmer_coef)<<8) + data[(j*w+i)*3+0]/dimmer_coef);
      }
      if(bDontDrawWhite)
      {
        // don't draw white
        if( data[(j*w+i)*3+2]>240 && data[(j*w+i)*3+1]>240 && data[(j*w+i)*3+0]>240 )
        {
          color = CRGB::Black;
        }
      }
      // une ligne sur 2 est inversée
      if((j%2)==0)
        leds[i+j*16] = color;
      else
        leds[(15-i)+j*16] = color;
    }
  }
  FastLED.show();
}

void loop()
{ 
  if( 1 )
  {
    full_on();
    delay(3000);
    //return;
  }

  if( 1 )
  {
    erase_all();
    full_one_color(CRGB::White);
    delay(3000);
    //return;
  }

  if( 1 )
  {
    erase_all();
    full_one_color(CRGB::Blue);
    delay(3000);
    //return;
  }

  if( 1 )
  {
    erase_all();
    full_one_color(CRGB::Red);
    delay(3000);
    //return;
  }

  if( 1 )
  {
    erase_all();
    full_one_color(CRGB::Green);
    delay(3000);
    //return;
  }

  if( 0 )
  {
    drawbitmap16x16(heart);
    //drawbitmap16x16(mario_body_bitmap);
    delay(1000);
    erase_all();
    drawImgs(aImgs_1,IMG_1_SIZE_X,IMG_1_SIZE_Y,0,32);
    delay(3000);
    erase_all();
    for(int i = 0; i < 8; ++i)
    {
      drawImgs(aImgs_2,IMG_2_SIZE_X,IMG_2_SIZE_Y,1,32);
      delay(500);
      drawImgs(aImgs_3,IMG_3_SIZE_X,IMG_3_SIZE_Y,1,32);
      delay(500);
    }
    for(int i = 0; i < 8; ++i)
    {
      drawImgs(aImgs_4,IMG_4_SIZE_X,IMG_4_SIZE_Y,1,32);
      delay(500);
      drawImgs(aImgs_5,IMG_5_SIZE_X,IMG_5_SIZE_Y,1,32);
      delay(500);
    }
    for(int i = 0; i < 8; ++i)
    {
      drawImgs(aImgs_6,IMG_6_SIZE_X,IMG_6_SIZE_Y,1,32);
      delay(500);
      drawImgs(aImgs_7,IMG_7_SIZE_X,IMG_7_SIZE_Y,1,32);
      delay(500);
    }
    return;
  }

  if( 0 )
  {
    for(int i = 0; i < 10; ++i )
    {
      chaser(10);
    }
  }

  if( 1 )
  {
    for(int i = 0; i < 3; ++i )
    {
      medusa(100);
    }
  }

  if( 1 )
  {
    for(int i = 0; i < 5; ++i )
    {
      serialGlow(100);
    }
  }

  if( 0 )
  {
    for(int i = 0; i < 2000; ++i )
    {
      strobo(20);
    }
  }

  if( 0 )
  {
    for(int i = 0; i < 32; ++i )
    {
      beat(120);
    }
  }

  static int32_t last = 0;
  Serial.println(millis()-last);
  last = millis();
}
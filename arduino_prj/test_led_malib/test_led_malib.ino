const int nFirstLedPin = 50; // one led per reader // 50 // 42

#include "Ai_WS2811.h"

const int nNbrReader = 2;
#define NUM_PIXELS 16
Ai_WS2811 aWs2811[nNbrReader];
struct CRGB * apLeds[nNbrReader] = {NULL, NULL};

void setup()
{
  int i;
  Serial.begin(115200);


  for( i = 0; i < nNbrReader; ++i )
  {
    aWs2811[i].init(nFirstLedPin+i,NUM_PIXELS);
    apLeds[i] = (struct CRGB*)aWs2811[i].getRGBData();
    aWs2811[i].setDim( 1 );
  }
  aWs2811[0].reducePixelNumber( 4 );  
  aWs2811[1].reducePixelNumber( 4 );
  aWs2811[2].reducePixelNumber( 4 );  
  
}

void animate_rainbow_mode()
{
  static int static_nHueColor = 0;
  const int nCoefRalentisseur = 16;

  Serial.println("rainbow");
  
  int i;
  for( i = 0; i < nNbrReader; ++i )
  {
    for( int j = 0; j < aWs2811[i].getPixelNumber(); ++j )
    {
      aWs2811[i].setHue( j, static_nHueColor/nCoefRalentisseur ); // not optimal: recomputing many times, same rgbs
    }
    aWs2811[i].sendLedData();
  }
  ++static_nHueColor;
  if( static_nHueColor >= 255*nCoefRalentisseur )
  {
    static_nHueColor = 0;
  }
}

void loop()
{
  animate_rainbow_mode();
  delay(10);
}

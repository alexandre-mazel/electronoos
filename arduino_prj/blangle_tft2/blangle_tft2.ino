// install tft_espi using the library manager
// or  copy TFT_eSPI-2.5.0.zip into 
// to C:\Users\alexa\Documents\Arduino\libraries

#include <TFT_eSPI.h>
#include <SPI.h>

//#define TFT_PARALLEL_8_BIT
//#define ILI9486_DRIVER
// try TFT_HX8357

TFT_eSPI tft = TFT_eSPI();

void setup()
{
  Serial.begin(9600);
  Serial.println("setup...");
  tft.init();
  tft.setRotation(3);
  tft.fillScreen(0x0);
}

void loop()
{
  Serial.println("loop blagngle2...");
  int r;

  tft.fillScreen(0x255);
  delay(1000); 
  tft.fillScreen(0x255);
  delay(1000);

  for( r = 0; r <= 0x1f; r++ )
  {
    tft.drawLine(0,r, 639, r, (r/2) );
    tft.drawLine(0,0x20*2+r, 639, 0x20*2+r, ((r/2)<<6) ); 
  }
  
}
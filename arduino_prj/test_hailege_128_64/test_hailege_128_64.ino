#include "oled.h"       // **** OLED ****

OLED display(20,21,NO_RESET_PIN,OLED::W_128,OLED::H_64,OLED::CTRL_SH1106,0x3C);

#define DISP(x,y,z) display.drawString(x,y,z)

void setup()
{
  Serial.begin(9600);
  Serial.println("Setup start");
  display.begin();
  display.set_contrast(8); // the eye doesn't register big difference, but power consumptions is
  display.set_scrolling(OLED::NO_SCROLLING);
  Serial.println("Setup end");
}

void loop()
{
  //Serial.println("looping...");
  if(0)
  {
    // des petits ronds
    for(int i = 0; i < 10; ++i)
    {
      display.draw_circle(7+i*10,5,5); // 7+ car sinon le rond n'est pas entier, pourquoi on peut pas dessiner en 0,0 ?
      display.draw_pixel(7+i*10,5);
    }
    display.display();
  }
  if(0)
  {
    // full blanc
    for(int j = 0; j < 64; ++j)
    {
      for(int i = 0; i < 128; ++i)
      {
        display.draw_pixel(i,j);
      }
    }
    display.display();
  }
  if(1)
  {
    DISP(0,0,"Start");
    DISP(0,1,"Autre message");
    DISP(6,4,"Hello World");
    display.display();
  }

  //Serial.println("sleeping...");
  delay(10);
}
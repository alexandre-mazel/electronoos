#include "oled.h"       // **** OLED ****

OLED display(20,21,NO_RESET_PIN,OLED::W_128,OLED::H_64,OLED::CTRL_SH1106,0x3C);

#define DISP(x,y,z) display.drawString(x,y,z);display.display()

void setup()
{
  Serial.begin(9600);
  Serial.println("Setup start");
  display.begin();
  display.set_scrolling(OLED::NO_SCROLLING);
  Serial.println("Setup end");
}

void loop()
{
  //Serial.println("looping...");
  for(int i = 0; i < 10; ++i)
  {
    display.draw_circle(5+i*10,5,5);
  }
  //DISP(0,0,"start");
  //DISP(6,8,"Hello World");
  display.display();
  //Serial.println("sleeping...");
  delay(10);
}
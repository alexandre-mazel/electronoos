#include "oled.h"       // **** OLED ****

OLED disp(20,21,NO_RESET_PIN,OLED::W_128,OLED::H_64,OLED::CTRL_SH1106,0x3C);

#define DISP(x,y,z) disp.drawString(x,y,z)

#define PIN_VOLT_MEASURE A0

void setup()
{
  Serial.begin(9600);
  Serial.println("- Solar Manager -");
  Serial.println("v0.3");
  Serial.println("Setup start");
  disp.begin();
  disp.set_contrast(8); // the eye doesn't register big difference, but power consumptions is
  disp.set_scrolling(OLED::NO_SCROLLING);
  Serial.println("Setup end");
}

void loop()
{
  //Serial.println("looping...");

  int nVoltRead = analogRead(PIN_VOLT_MEASURE);
  float rVoltResult = nVoltRead*5/1024 * 85/10;

  char result[8];
  char line[24] = "";
  dtostrf(rVoltResult, 6, 2, result);
  strcat(line," Puis:");
  strcat(line, result);
  strcat(line, "V        ");

  //disp.clear();
  disp.draw_rectangle(32,8,90,20,OLED::SOLID,OLED::BLACK); // au lieu d'effacer tout l'ecran on efface juste cette zone

  DISP(0,0,"- Solar Manager -");
  DISP(0,1,line);
  DISP(0,7,"Bas de l'ecran");
  disp.display();


  //Serial.println("sleeping...");
  delay(10);
}
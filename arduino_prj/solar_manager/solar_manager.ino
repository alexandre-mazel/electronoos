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

unsigned long timeEnoughPower = 0; // en millis (wrap around after 49 days)
unsigned long timeStartEnough = 0; // start time with enough power (usefull to compute duration), set to 0 if not enough power 

void loop()
{
  //Serial.println("looping...");

  int nVoltRead = analogRead(PIN_VOLT_MEASURE);
  float rVoltResult = nVoltRead*5/1024 * 85/10;

  

  //disp.clear();

  DISP(0,0,"- Solar Manager -");
    char result[8];
  char line[24] = "";
  dtostrf(rVoltResult, 6, 2, result);
  strcat(line,"Puis:");
  strcat(line, result);
  strcat(line, "V        ");
  disp.draw_rectangle(32,8,90,20,OLED::SOLID,OLED::BLACK); // au lieu d'effacer tout l'ecran on efface juste cette zone
  DISP(0,1,line);

  line[0] = '\0';
  ltoa(timeEnoughPower/1000, result, 10);
  strcat(line,"Enough: ");
  strcat(line, result);
  strcat(line, "s        ");
  DISP(0,2,line);

  line[0] = '\0';
  ltoa(millis()/1000, result, 10);
  strcat(line,"Elapsed: ");
  strcat(line, result);
  strcat(line, "s        ");
  disp.draw_rectangle(32,8,90,20,OLED::SOLID,OLED::WHITE);
  DISP(0,3,line);

  DISP(0,7,"Bas de l'ecran");
  disp.display();


  //Serial.println("sleeping...");
  delay(10);
}
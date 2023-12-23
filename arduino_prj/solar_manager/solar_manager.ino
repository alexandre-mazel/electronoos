#include "oled.h"       // **** OLED ****
#include "historic.h"

OLED disp(20,21,NO_RESET_PIN,OLED::W_132,OLED::H_64,OLED::CTRL_SH1106,0x3C); // si je met CTRL_SSD1306 ca scroll tout le temps, et si je met CTRL_SH1106 ya du garbage a droite

Historic hist(120);

/*
//U8X8_SSD1306_128X64_NONAME_HW_I2C disp(U8X8_PIN_NONE);    //use this line for standard 0.96" SSD1306
U8X8_SH1106_128X64_NONAME_HW_I2C disp(U8X8_PIN_NONE);       //use this line for 1.3" OLED often sold as 1.3" SSD1306
*/

#define DISP(x,y,z) disp.drawString(x,y,z)

#define PIN_VOLT_MEASURE A0

char * smartMillisToString(unsigned long millisec, char * dst)
{
  // convert secong to a smart string
  if(millisec < 1000)
  {
    ltoa(millisec,dst,10);
    strcat(dst,"ms");
    return dst;
  }
  millisec /= 1000;
  if(millisec < 60)
  {
    ltoa(millisec,dst,10);
    strcat(dst,"s");
    return dst;
  }

  // now we want 1 figure after commat
  float t = millisec/60.;
  if(t<60)
  {
    dtostrf(t, 0, 1, dst);
    strcat(dst,"m");
    return dst;
  }

  t = millisec/60.;
  if(t<60)
  {
    dtostrf(t, 0, 1, dst);
    strcat(dst,"h");
    return dst;
  }

  t = millisec/60.;
  dtostrf(t, 0, 1, dst);
  strcat(dst,"day");
  return dst;
}

void setup()
{
  Serial.begin(9600);
  Serial.println("- Solar Manager -");
  Serial.println("v0.3");
  Serial.println("Setup start");
  disp.useOffset(1);
  disp.begin();
  disp.set_contrast(8); // the eye doesn't register big difference, but power consumptions is
  //disp.set_scrolling(OLED::NO_SCROLLING);
  disp.clear();
  Serial.println("Setup end");
}

unsigned long timeEnoughPower = 0; // en millis (wrap around after 49 days)
unsigned long timeStartEnough = 0; // start time with enough power (usefull to compute duration), set to 0 if not enough power

void loop()
{
  //Serial.println("looping...");

  // computing
  int nVoltRead = analogRead(PIN_VOLT_MEASURE);
  float rVoltResult = nVoltRead*5/1024 * 85/10;
  unsigned long timeEnoughPowerEstimated = timeEnoughPower;

  hist.append(int(rVoltResult));
  if(rVoltResult>10)
  {
    if(timeStartEnough == 0)
    {
      timeStartEnough = millis();
    }
    else
    {
      // do nothing
      timeEnoughPowerEstimated += millis()-timeStartEnough;
    }
  }
  else
  {
    
    if(timeStartEnough != 0)
    {
      // first time without enough power
      timeEnoughPower += millis()-timeStartEnough; // we want to be quite accurate on adding time, so we dont inc every time
      timeStartEnough = 0;
    }
  }

  

  //disp.clear();

  DISP(0,0,"- Solar Manager -");
  char result[10];
  char line[24] = "";
  dtostrf(rVoltResult, 6, 2, result);
  strcat(line,"Puis:");
  strcat(line, result);
  strcat(line, "V        ");
  disp.draw_rectangle(32,8,90,20,OLED::SOLID,OLED::BLACK); // au lieu d'effacer tout l'ecran on efface juste cette zone
  DISP(0,1,line);

  line[0] = '\0';
  ltoa(timeEnoughPowerEstimated/1000, result, 10);
  strcat(line,"Enough: ");
  strcat(line, result);
  strcat(line, "s        ");
  disp.draw_rectangle(40,16,90,23,OLED::SOLID,OLED::BLACK);
  DISP(0,2,line);

  line[0] = '\0';
  ltoa(millis()/1000, result, 10);
  strcat(line,"Elapsed: ");
  //strcat(line, result);
  //strcat(line, "s        ");
  smartMillisToString(millis(),result);
  strcat(line, result);
  disp.draw_rectangle(40,24,90,32,OLED::SOLID,OLED::BLACK);
  DISP(0,3,line);

  DISP(0,7,"Bas de l'ecran");


  hist.sendToOled(0,32,&disp);

  disp.display();




  //Serial.println("sleeping...");
  delay(1000); // 1000 is nice for historisation
}
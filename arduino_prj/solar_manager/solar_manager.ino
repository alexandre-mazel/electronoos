#include "oled.h"       // **** OLED ****
#include "historic.h"

OLED disp(20,21,NO_RESET_PIN,OLED::W_132,OLED::H_64,OLED::CTRL_SH1106,0x3C); // si je met CTRL_SSD1306 ca scroll tout le temps, et si je met CTRL_SH1106 ya du garbage a droite

Historic hist(128); // good to put screen resolution

/*
//U8X8_SSD1306_128X64_NONAME_HW_I2C disp(U8X8_PIN_NONE);    //use this line for standard 0.96" SSD1306
U8X8_SH1106_128X64_NONAME_HW_I2C disp(U8X8_PIN_NONE);       //use this line for 1.3" OLED often sold as 1.3" SSD1306
*/

#define DISP(x,y,z) disp.drawString(x,y,z)

#define PIN_VOLT_MEASURE A0
#define PIN_CURRENT_MEASURE A1

#define ACS712_MAX_CURRENT 25

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

int nFpsCpt = 0;
unsigned long timeFpsBegin = 0;

// measure input and return filtered value (on 4)
float rVoltResultAvg = 0.f;
float rVoltResultAvg5 = 0.f;

// A 4 measures per sec, 1200 => 5min 
// (sauf que je me souviens plus pourquoi mais vu ma formule, ca prend plutot 20min a atteindre la cible, alors on va diviser tout ca)
const int nNbrFor5 = 1200/5;

float rVoltResultAvg20 = 0.f;
const int nNbrFor20 = nNbrFor5*4;
float measureSolarOutput()
{
  int nVoltRead = analogRead(PIN_VOLT_MEASURE);
  float rVoltResult = (nVoltRead*5.*85)/(1024*10);
  rVoltResult *= 1.013; // avec les resistances 750k a 5% que j'ai prise, j'ai cette modif a appliquer (mesure calculé sur 31V)
  rVoltResultAvg = rVoltResultAvg * 0.75 + rVoltResult * 0.25;
  rVoltResultAvg5 = (rVoltResultAvg5 * (nNbrFor5-1)/nNbrFor5) + (rVoltResult * (1)/nNbrFor5);
  rVoltResultAvg20 = (rVoltResultAvg20 * (nNbrFor20-1)/nNbrFor20) + (rVoltResult * (1)/nNbrFor20);
  return rVoltResultAvg;
}

float measureAmp()
{
  int nVoltRead = analogRead(PIN_CURRENT_MEASURE);
  float rAmpResult = (nVoltRead*ACS712_MAX_CURRENT)/(1024.);
  return rAmpResult;
}

void loop()
{
  //Serial.println("looping...");

  float rVoltResult = measureSolarOutput();
  unsigned long timeEnoughPowerEstimated = timeEnoughPower;

  float rAmpResult = measureAmp();

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
  char line[48] = "";
  dtostrf(rVoltResult, 5, 2, result);
  strcat(line,"Puis:");
  strcat(line, result);
  strcat(line, "V");
  if(1)
  {
    // add avg 5 et 20min
    strcat(line, "/");
    dtostrf(rVoltResultAvg5, 0, 1, result);
    strcat(line, result);

    strcat(line, "/");
    dtostrf(rVoltResultAvg20, 0, 1, result);
    strcat(line, result);

  }
  disp.draw_rectangle(32,8,90+38,15,OLED::SOLID,OLED::BLACK); // au lieu d'effacer tout l'ecran on efface juste cette zone
  DISP(0,1,line);

  line[0] = '\0';
  
  strcat(line,"Enough: ");
  //ltoa(timeEnoughPowerEstimated/1000, result, 10);
  //strcat(line, result);
  //strcat(line, "s        ");
  smartMillisToString(timeEnoughPowerEstimated,result);  // not longer than ltoa(timeEnoughPowerEstimated/1000, result, 10) (even less!?!)
  strcat(line, result);
  disp.draw_rectangle(40,16,90,23,OLED::SOLID,OLED::BLACK);
  DISP(0,2,line);

  line[0] = '\0';
  strcat(line,"Elapsed: ");
  //ltoa(millis()/1000, result, 10);
  //strcat(line, result);
  //strcat(line, "s        ");
  smartMillisToString(millis(),result);
  strcat(line, result);
  disp.draw_rectangle(40,24,90,32,OLED::SOLID,OLED::BLACK);
  DISP(0,3,line);

  //DISP(0,7,"Bas de l'ecran");


  hist.drawGraphicOled(0,64,&disp,32);

  disp.display(); // takes around 340ms on a mega2560!


  //Serial.println("sleeping...");
  //delay(10); 
  // the goal is to cut the wait in 3 parts, measuring between each part
  const int nTotalWait = 620; // 1s is nice for historisation, rendering takes 380 so putting 620 is nice...
  const int nNbrMeasures = 3;
  for( int i = 0; i < nNbrMeasures; i += 1)
  {
    measureSolarOutput();
    delay(nTotalWait/nNbrMeasures); 
  }

  ++nFpsCpt;
  const int nNbrFrameToCompute = 10;
  if( nFpsCpt == nNbrFrameToCompute )
  {
    unsigned long nNow = micros();
    unsigned long nDuration = nNow - timeFpsBegin;
    
    Serial.print( "frame: " );
    Serial.print( nDuration/nNbrFrameToCompute );
    Serial.print( "us, fps: " );
    Serial.println( 1000000.*nNbrFrameToCompute/nDuration );
    timeFpsBegin = nNow;
    nFpsCpt = 0;
    
    // a simple analog read is running at 5413fps (184us per frame)
  }
}
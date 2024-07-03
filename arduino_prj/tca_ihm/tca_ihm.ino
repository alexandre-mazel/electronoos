#include <LiquidCrystal.h>

#define PIN_POTAR_BASE  A10 // first pin of the series
#define PIN_SW_BASE     30
#define PIN_SWTRI_BASE  40


#define NBR_POTAR   3
#define NBR_SW      4
#define NBR_SWTRI   3

#define NBR_SENSORS (NBR_POTAR+NBR_SW+NBR_SWTRI*2)


#include <LiquidCrystal_I2C.h>

bool i2CAddrTest(uint8_t addr) {
  Wire.begin();
  Wire.beginTransmission(addr);
  if (Wire.endTransmission() == 0) {
    return true;
  }
  return false;
}

LiquidCrystal_I2C * pLcd = NULL;

#define DEBUG Serial
unsigned long fpsTimeStart = 0;
unsigned long fpsCpt = 0;
void countFps()
{
  fpsCpt += 1;

  // optim: don't read millis at everycall
  // gain 1.1micros per call (averaged)
  // an empty loop takes 67.15micros on mega2560 (just this function)

  if((fpsCpt&7)!=7)
  {
    return;
  }  

  unsigned long diff = millis() - fpsTimeStart;
  if (diff > 5000)
  {
    //unsigned long timeprintbegin = micros();
    float fps = (float)(fpsCpt*1000)/diff;
    DEBUG.print("fps: ");
    DEBUG.print(fps);
    DEBUG.print(", dt: ");
  #if 1
    {
      DEBUG.print(1000.f/fps,3);
      DEBUG.println("ms");
    }
#else
    {
      DEBUG.print(1000000.f/fps);
      DEBUG.println("micros");
    }
#endif

    fpsTimeStart = millis();
    fpsCpt = 0;
    //unsigned long durationprint = micros()-timeprintbegin;
    //DEBUG.print("duration fps micros: "); // 1228micros at 57600baud !!!, 1280 at 115200 (change nothing, it's more the time to compute)
    //DEBUG.println(durationprint);
  }

}

void setup()
{
  Serial.begin(57600);

  for( int i = 0; i < NBR_POTAR; ++i )
  {
    pinMode( PIN_POTAR_BASE+i, INPUT );
  }

  for( int i = 0; i < NBR_SW; ++i )
  {
    pinMode( PIN_SW_BASE+i, INPUT );
  }

  for( int i = 0; i < NBR_SWTRI*2; ++i )
  {
    pinMode( PIN_SWTRI_BASE+i, INPUT );
  }

  uint8_t i2cAddr = 0x3F;
  if(!i2CAddrTest(i2cAddr))
  {
    i2cAddr = 0x27;
  }

  Serial.print("DBG: Using LCD at I2C Addr: 0x");
  Serial.println(i2cAddr,HEX);

  pLcd = new LiquidCrystal_I2C(i2cAddr, 20, 4); // 0x3F sur la version de base, 0x27 sur la version oversized

  pLcd->init();                // initialize the lcd
  pLcd->backlight();           // Turn on backlight // sans eclairage on voit rien...
  
  Serial2.begin(57600);

  pLcd->print("Setup started...");
}


// same as print, but add some space after msg to clean previous string

void lcdPrint(const char * msg)
{
  pLcd->print(msg);
  if(strlen(msg)<20)
    pLcd->print(" ");
  if(strlen(msg)<19)
    pLcd->print(" ");
}


void sendSerialCommand(const char * msg)
{
  Serial2.print("##");
  Serial2.println(msg);
  //char buf[32];
  //snprintf
  //Serial.println(millis());

  pLcd->setCursor(0, 3);
  lcdPrint(msg);
}


void drawCharsTable()
{
  for(int page=0;page<4;++page)
  {
    pLcd->setCursor(0, 0);
    for(int i = 0; i < 64; ++i)
    {
      char buf[2];
      buf[0] = (char)i+page*64;
      buf[1] = '\0';
      pLcd->setCursor(i%16, i/16);
      pLcd->print(buf);
    }
    delay(5000);
  }
}

void lcdPrintChar(unsigned char ch)
{
  char buf[2];
  buf[0] = (char)ch;
  buf[1] = '\0';
  pLcd->print(buf);
}

// print always on 4 chars
void lcdPrint(float r)
{
  if(abs(r)<10)
  {
    if((float)(int)r != r)
    {
      // with decimals
      pLcd->print(r,2);
    }
    else
    {
      // decimals are null, print with no decimals
      pLcd->print("   ");
      pLcd->print(r,0);
    }
    return;
  }
  if(abs(r)<100)
  {
    if((float)(int)r != r)
    {
      // with 1 decimal
      pLcd->print(r,1);
    }
    else
    {
      pLcd->print("  ");
      pLcd->print(r,0);
    }
    return;
  }
  if(r<1000)
  {
    pLcd->print(" ");
  }
  pLcd->print(int(r));
  return;
  
}

float rNbrTwist = 0;
float rNbrTwistLimit = 1000;
int nNbrTwistSpeed = 500;
float rNbrCollect = 0;
float rNbrCollectLimit = 1000;
int nNbrCollectSpeed = 100;
float rNbrSpool = 0;
float rNbrSpoolLimit = 1000;
int nNbrSpoolSpeed = 100;

// array of pointer to help algorithm and settings
int * apnSpeedArray[] = {&nNbrTwistSpeed,&nNbrCollectSpeed,&nNbrSpoolSpeed};


int nNumLineEdited = 3;
float * prEdited = &rNbrTwist;
int nNbrFrame = 0;

bool bMotor1_sign = 0;

bool bPrevPush1 = 0;
bool bPrevPush2 = 0;

int anPrevReadValues[NBR_SENSORS];

void loop()
{
  // char buf[16];
  //drawCharsTable();

  int anReadValues[NBR_SENSORS];


  for( int i = 0; i < NBR_POTAR; ++i )
  {
    anReadValues[i] = analogRead(PIN_POTAR_BASE+i);
    if(anReadValues[i] != anPrevReadValues[i])
    {
      if(i<1)
        *(apnSpeedArray[i]) = (int)( (anReadValues[i] *1000L) / 1023);
      else
        *(apnSpeedArray[i]) = (int)( (anReadValues[i] *300L) / 1023);
    }
  }

  for( int i = 0; i < NBR_SW; ++i )
  {
    anReadValues[i+NBR_POTAR] = digitalRead(PIN_SW_BASE+i) == HIGH;
  }

  for( int i = 0; i < NBR_SWTRI*2; ++i )
  {
    anReadValues[i+NBR_POTAR+NBR_SW] = digitalRead(PIN_SWTRI_BASE+i) == HIGH;
  }

  memcpy(anPrevReadValues,anReadValues,sizeof(anPrevReadValues));


 // Serial.println(digitalRead(PIN_SW_BASE+0) == HIGH);

  if((nNbrFrame%20)==0)
  {
    // debug
    Serial.print("DBG: values: ");
    for( int i = 0; i < NBR_SENSORS; ++i )
    {
      if(i<NBR_POTAR)
      {
        Serial.print("POT");
        Serial.print(i);
      }
      else if(i<NBR_POTAR+NBR_SW)
      {
        Serial.print("SW");
        Serial.print(i-NBR_POTAR);
      }
      else
      {
        Serial.print("SWTRI");
        Serial.print(i-NBR_POTAR-NBR_SW);
      }
      Serial.print(": ");
      Serial.print(anReadValues[i]);
      Serial.print(", ");
    }
    Serial.println("");

  }
  
  if(1)
  {
    // update lcd (takes 57ms) - when 3 lines
    pLcd->setCursor(0, 0);
    pLcd->print("Twi ");
    lcdPrint(rNbrTwist);
    pLcd->print("/");
    lcdPrint(rNbrTwistLimit);
    pLcd->print("");
    lcdPrint(nNbrTwistSpeed);
    pLcd->print("rpm");

    pLcd->setCursor(0, 1);
    pLcd->print("Col ");
    lcdPrint(rNbrCollect);
    pLcd->print("/");
    lcdPrint(rNbrCollectLimit);
    pLcd->print("");
    lcdPrint(nNbrCollectSpeed);
    pLcd->print("rpm");

    pLcd->setCursor(0, 2);
    pLcd->print("Spo ");
    lcdPrint(rNbrSpool);
    pLcd->print("/");
    lcdPrint(rNbrSpoolLimit);
    pLcd->print("");
    lcdPrint(nNbrSpoolSpeed);
    pLcd->print("rpm");

    pLcd->setCursor(19, nNumLineEdited);
    lcdPrintChar(127);
  }

  ++nNbrFrame;
  delay(10);
  countFps();
}

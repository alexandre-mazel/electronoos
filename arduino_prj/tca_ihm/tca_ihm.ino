#include <LiquidCrystal.h>

#define PIN_POTAR1  A15
#define PIN_SW1 42
#define PIN_SW2 40

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

  pinMode(PIN_POTAR1, INPUT);
  pinMode(PIN_SW1, INPUT);
  pinMode(PIN_SW2, INPUT);

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
    pLcd->print(r,2);
    return;
  }
  if(abs(r)<100)
  {
    pLcd->print(r,1);
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
float rNbrCollect = 0;
int nNbrCollectSpeed = 100;
float rNbrSpool = 0;

int nNumLineEdited = 0;
float * prEdited = &rNbrTwist;
int nNbrFrame = 0;

bool bMotor1_sign = 0;

bool bPrevPush1 = 0;
bool bPrevPush2 = 0;

void loop()
{
  // char buf[16];
  //drawCharsTable();

  int pushed1 = digitalRead(PIN_SW1) == HIGH;
  int pushed2 = digitalRead(PIN_SW2) == HIGH;
  int nPotar1 = 1023-analogRead(PIN_POTAR1);

  if((nNbrFrame%20)==0)
  {
    // debug
    Serial.print("DBG: sw1: "); Serial.print(pushed1); Serial.print(", sw2: "); Serial.print(pushed2); Serial.print(", nPotar1: "); Serial.println(nPotar1);
  }
  

  if(1)
  {
    // update value from potar
    float rInc = 0.0f;
    // mid is 512
    if(nPotar1<400)
    {
      rInc = -(400-nPotar1)/400.f;
    }
    else if(nPotar1>623)
    {
      rInc = (nPotar1-623)/500.f;
    }

    *prEdited += rInc*rInc*rInc*30;
  }

  if(bPrevPush1 != pushed1)
  {
    bPrevPush1 = pushed1;
    if(pushed1 )
    {
      *prEdited += 1000;
      bMotor1_sign = 1;
      sendSerialCommand("MOTOR_1_1_500");
    }
  }
  
  if(bPrevPush2 != pushed2)
  {
    bPrevPush2 = pushed2;
    if(pushed2)
    {
      *prEdited -= 1000;
      bMotor1_sign = -1;
      sendSerialCommand("MOTOR_1_-1_50");
    }
  }

  if(1)
  {
    // update lcd (takes 57ms)
    pLcd->setCursor(0, 0);
    pLcd->print("Twi ");
    lcdPrint(rNbrTwist);
    pLcd->print("   ");

    pLcd->setCursor(0, 1);
    pLcd->print("Col ");
    lcdPrint(rNbrCollect);
    pLcd->print("/");
    pLcd->print(nNbrCollectSpeed);
    pLcd->print("rpm");

    pLcd->setCursor(0, 2);
    pLcd->print("Spo ");
    lcdPrint(rNbrSpool);
    pLcd->print("   ");

    pLcd->setCursor(19, nNumLineEdited);
    lcdPrintChar(127);
  }

  ++nNbrFrame;
  delay(10);
  countFps();
}

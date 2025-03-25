#include <LiquidCrystal.h>

#define PIN_POTAR_BASE  A10 // first pin of the series
#define PIN_SW_BASE     30
#define PIN_SWTRI_BASE  40


#define NBR_POTAR   3
#define NBR_SW      4
#define NBR_SWTRI   3

#define NBR_SENSORS (NBR_POTAR+NBR_SW+NBR_SWTRI*2)

#define NBR_MOTORS  3

#define PIN_DIST_IR 8 // 8 is for D8


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

  pinMode( PIN_DIST_IR, INPUT );
  
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

int16_t avg_dist = 0;

int16_t get_dist_ir( const int nPin )
{
  int16_t t = pulseIn(nPin, HIGH);
 
  if (t == 0)
  {
    // pulseIn() did not detect the start of a pulse within 1 second.
    Serial.println("timeout");
    return -1;
  }

  if (t > 1850)
  {
    // No detection.
    Serial.println(-1);
    return -1;
  }

  // Valid pulse width reading. Convert pulse width in microseconds to distance in millimeters.
  int16_t dist = (t - 1000) * 4;

  // Limit minimum distance to 0.
  if (dist < 0) { dist = 0; }

  // cf pololu_dist_IR for explaination

  //dist = (dist + 28.416 ) / 1.7241;
  dist = (dist + 2 ) / 1.70; // based on pololu_distance_measurement_reglin.py en s'arretant a 700 (inclus)
  //dist = (dist + 20 ) / 1.77; // based on pololu_distance_measurement_reglin.py en s'arretant a 600 (inclus) (moins bon pour 100 mais meilleur pour les autres)


  avg_dist = ( avg_dist * 5 + dist * 1 ) / 6; // a 130cm de max, ca fait 1300mm, donc en max pour ne pas depasser int16, il ne faut pas filtrer a plus de 24

  return avg_dist;
}

float rNbrTwist = 0;
float rNbrTwistLimit = 1000;
int nNbrTwistSpeed = 500;
int nTwistDir = 0; // current moving of the twist motor: -1,0,1

float rNbrCollect = 0;
float rNbrCollectLimit = 1000;
int nNbrCollectSpeed = 100;
int nCollectDir = 0;

float rNbrSpool = 0;
float rNbrSpoolLimit = 1000;
int nNbrSpoolSpeed = 100;
int nSpoolDir = 0;

float dist_slider_min = 170+50; // could be int, but all settings functions are taking float
float dist_slider_max = 370-50;
const int nAutomaticSpoolRotationSpeedInit = 30;
int nAutomaticSpoolRotationSpeed = nAutomaticSpoolRotationSpeedInit;
bool bAutomaticSpoolMode = 0;
long int timeNextAutomaticSpoolSpeedChangePossible = 0;  // we don't want to change speed to often

float dist_slider_target = 500; // was 270
int last_dist_slider = -1;
long int last_time_dist_pos = millis();

// array of pointer to help algorithm and settings
float * aprPosArray[] = {&rNbrTwist,&rNbrCollect,&rNbrSpool,&dist_slider_min,&dist_slider_max};
float * aprLimitArray[] = {&rNbrTwistLimit,&rNbrCollectLimit,&rNbrSpoolLimit};
int * apnSpeedArray[] = {&nNbrTwistSpeed,&nNbrCollectSpeed,&nNbrSpoolSpeed};
int * apnDirArray[] = {&nTwistDir,&nCollectDir,&nSpoolDir};
// Switch routing
int   anSwIndex[] = {2, 0, 1, 3}; // order is turbo, select, +, -
// TriSwich routing
int   anTriSwIndex[] = {2,0,1}; // how ordered are the triswitch compared to the motor number, anTriIndex[2] = 0 => the third tri switch is related to the twisting motor
int   anTriSwInverted[] = {-1,1,1}; // invert direction (miscabled) anTriSwInverted[0] = -1: the first switch is reverted

int nNumLineEdited = 3;
float * prEdited = aprLimitArray[0];
int nNbrFrame = 0;

bool bMotor1_sign = 0;

bool bPrevPush1 = 0;
bool bPrevPush2 = 0;

bool bTurboIsOn = 0;

int anPrevReadValues[NBR_SENSORS];

long int nPrevTimeIntoLoop = 0;

void loop()
{
  // char buf[16];
  //drawCharsTable();
  const int nSizeBuf = 24;
  char buf[nSizeBuf+1];
  int anReadValues[NBR_SENSORS];

  int abSendMotorChange[] = {0,0,0};


  for( int i = 0; i < NBR_POTAR; ++i )
  {
    anReadValues[i] = analogRead(PIN_POTAR_BASE+i);
    if(abs(anReadValues[i] - anPrevReadValues[i])>1) // avoid spurious change
    {
      if(i<2)
      {
        int nVal = (int)( (anReadValues[i] *512L) / 1023);
        nVal = (nVal / 4) * 4; // put entire step to help have same on both
        *(apnSpeedArray[i]) = nVal;
      }
      else
      {
        if( bTurboIsOn ) // no change of speed when turbo is on (prevent bug: turbo is disabled by spurious potar change)
        {
          continue;
        }
        if( bAutomaticSpoolMode )
        {
          continue; // no change of potar when automatic spooling
        }
        *(apnSpeedArray[i]) = (int)( (anReadValues[i] *256L) / 1023); // put less to have more precision (was 20L)
      }
      if(*apnDirArray[i] != 0)
        abSendMotorChange[i] = 1;
    }
  }

  for( int i = 0; i < NBR_SW; ++i )
  {
    anReadValues[i+NBR_POTAR] = digitalRead(PIN_SW_BASE+i) == HIGH;
    if(anReadValues[i+NBR_POTAR] != anPrevReadValues[i+NBR_POTAR])
    {
      int nSwitch = anSwIndex[i];
      if (nSwitch == 0)
      {
        // turbo
        if( nSpoolDir != 0 )
        {
          int nMotor = 2;
          
          if( 0 )
          {
            // mode turbo is engaged just when pushing
            int nTurbo = 4; // decide the turbo ratio
            if(anReadValues[i+NBR_POTAR] == 0)
            {
              nTurbo = 1;
            }
            snprintf(buf,nSizeBuf, "MOTOR_%d_%d_%d",nMotor,nSpoolDir,*apnSpeedArray[nMotor]*nTurbo);
            sendSerialCommand(buf);
          }
          else
          {
            // mode turbo is toggled by turbo switch
            if(anReadValues[i+NBR_POTAR] == 1)
            {
              bTurboIsOn = ! bTurboIsOn;
              int nNewSpeed = *apnSpeedArray[nMotor];
              if( bTurboIsOn )
              {
                nNewSpeed = 400;
              }
              snprintf(buf,nSizeBuf, "MOTOR_%d_%d_%d",nMotor,nSpoolDir,nNewSpeed);
              sendSerialCommand(buf);
            }
          }
        }
      }
      else if (nSwitch == 1 && anReadValues[i+NBR_POTAR] )
      {
        // select and reset laps
        for( int nMotor = 0; nMotor < NBR_MOTORS; ++nMotor )
        {
          *aprPosArray[nMotor] = 0;
        }
        nNumLineEdited += 1;
        nNumLineEdited %= 4;

        if( nNumLineEdited < 3 )
        {
          prEdited = aprLimitArray[nNumLineEdited];
        }
      }
      else if (nSwitch == 2 && anReadValues[i+NBR_POTAR] )
      {
        // up
        if( nNumLineEdited < 3 ) *prEdited += 100;

      }
      else if (nSwitch == 3 && anReadValues[i+NBR_POTAR] )
      {
        // down
        if( nNumLineEdited < 3 ) *prEdited -= 100;
      }
    }
  }

  for( int i = 0; i < NBR_SWTRI*2; ++i )
  {
    anReadValues[i+NBR_POTAR+NBR_SW] = digitalRead(PIN_SWTRI_BASE+i) == HIGH;
    int nMotor = anTriSwIndex[i/2];

    //Serial.print("mot: " ); Serial.print(nMotor); Serial.print(", sendchange:" ); Serial.println(abSendMotorChange[nMotor]);
    if(anReadValues[i+NBR_POTAR+NBR_SW] != anPrevReadValues[i+NBR_POTAR+NBR_SW] || (abSendMotorChange[nMotor]&&anReadValues[i+NBR_POTAR+NBR_SW]) ) // second &&, because we can enter the loop with the other direction of this triswitch
    {
      int nDirection = ((i%2)*2)-1;
      nDirection *= anTriSwInverted[nMotor];
      if(anReadValues[i+NBR_POTAR+NBR_SW] == 0)
      {
        nDirection = 0;
      }
      if( nMotor == 0 )
      {
        // when twisting it enables the automatic spool mode
        int bPrevAuto = bAutomaticSpoolMode;
        bAutomaticSpoolMode = nDirection != 0;
        if( bAutomaticSpoolMode != bPrevAuto )
        {
          if( ! bAutomaticSpoolMode )
          {
            // we stop the automatic spool mode so let's stop the spool motor !
            int nMotor = 2;
            int nDirection = 0;
            snprintf(buf,nSizeBuf, "MOTOR_%d_%d_%d",nMotor,nDirection,nAutomaticSpoolRotationSpeed);
            sendSerialCommand(buf);
          }
          else
          {
            nAutomaticSpoolRotationSpeed = nAutomaticSpoolRotationSpeedInit;
          }
        }
      }
      *apnDirArray[nMotor] = nDirection;
      snprintf(buf,nSizeBuf, "MOTOR_%d_%d_%d",nMotor,nDirection,*apnSpeedArray[nMotor]);
      sendSerialCommand(buf);
    }
  }

  int16_t dist_slider = get_dist_ir(PIN_DIST_IR);

  memcpy(anPrevReadValues,anReadValues,sizeof(anPrevReadValues));

  if( bAutomaticSpoolMode && millis() > timeNextAutomaticSpoolSpeedChangePossible )
  {
    // automatic speed rotation
    int nNewSpeed = nAutomaticSpoolRotationSpeed;
    const int nMinSpeed = 0;
    const int nMaxSpeed = 48;

    /*
    if( dist_slider > dist_slider_max )
    {
      nNewSpeed -= 2;
      if( nNewSpeed < nMinSpeed )
      {
        nNewSpeed = nMinSpeed;
      }
    }
    else if( dist_slider < dist_slider_min )
    {
      nNewSpeed += 4;
      if( nNewSpeed > nMaxSpeed )
      {
        nNewSpeed = nMaxSpeed;
      }
    }
    */

    if( abs(dist_slider_target-dist_slider) > 10 && abs(rNbrTwist) > 500 )
    {
      if( last_dist_slider !=-1 ) // not first time
      {
        long int diff = dist_slider - last_dist_slider;
        long int time_for_diff = millis() - last_time_dist_pos;
        float diff_per_sec = ( diff * 1000 ) / time_for_diff;
        int dist_bonus = 0;
        if( abs(dist_slider_target-dist_slider) > 20)
        {
          //dist_bonus = (abs(dist_slider_target-dist_slider) - 20)/4;
        }
        if( dist_slider < dist_slider_target  )
        {
          if( diff_per_sec < 0 )
          {
            // we need to do something to increase dist and so inc speed
            nNewSpeed += 2 + dist_bonus;
            if( nNewSpeed > nMaxSpeed )
            {
              nNewSpeed = nMaxSpeed;
            }
          }
        }
        else
        {
         if( diff_per_sec > 0 )
          {
            // we need to do something to decrease dist and so reduce speed
            nNewSpeed -= 2 + dist_bonus;
            if( nNewSpeed < nMinSpeed )
            {
              nNewSpeed = nMinSpeed;
            }
          }
        }
      } // not first time
      last_dist_slider = dist_slider;
      last_time_dist_pos = millis();
    }

    if( nNewSpeed != nAutomaticSpoolRotationSpeed )
    {
      Serial.print( "DBG: NEW spool speed: " );
      Serial.println( nNewSpeed );
      nAutomaticSpoolRotationSpeed = nNewSpeed;
      timeNextAutomaticSpoolSpeedChangePossible = millis() + 4000;
      int nMotor = 2;
      int nDirection = 1;
      snprintf(buf,nSizeBuf, "MOTOR_%d_%d_%d",nMotor,nDirection,nAutomaticSpoolRotationSpeed);
      sendSerialCommand(buf);
    }
  }


 // Serial.println(digitalRead(PIN_SW_BASE+0) == HIGH);

  if((nNbrFrame%20)==0)
  //if(0)
  {
    // debug buttons and potars
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

  if((nNbrFrame%20)==0)
  //if(0)
  {
    // debug nbr turn and dist
    Serial.print("DBG: pos motor: ");
    for( int nMotor = 0; nMotor < NBR_MOTORS; ++nMotor )
    {
      Serial.print(*aprPosArray[nMotor]);
      Serial.print(", ");
    }
    Serial.print("dist: ");
    Serial.print(dist_slider);
    Serial.print(", automatic: ");
    Serial.print(bAutomaticSpoolMode);
    Serial.println("");
  }

  //if(1)
  if((nNbrFrame%4)==0) // compute less to reduce computations errors
  {
    // estimate rotation of motors
    long int nDT = millis()-nPrevTimeIntoLoop; // will be more precise with micros, but we explode the long int with 60*1000*1000 (and LL doesn't change sth)
    nPrevTimeIntoLoop = millis();
    for( int nMotor = 0; nMotor < NBR_MOTORS; ++nMotor )
    {
      if(*apnDirArray[nMotor] == 0)
        continue;
      float rIncTurn = ( nDT * (*apnSpeedArray[nMotor]) * (*apnDirArray[nMotor]) ) / (60.f*1000);
      //Serial.println(rIncTurn);
      *aprPosArray[nMotor] += rIncTurn;

      if( *aprPosArray[nMotor] > *aprLimitArray[nMotor] )
      {
        snprintf(buf,nSizeBuf, "MOTOR_%d_%d_%d",nMotor,0,0);
        sendSerialCommand(buf);
        *apnDirArray[nMotor] = 0;
      }
    }
    
  }
  
  if(1)
  {
    // update lcd (takes 57ms) - when 3 lines
    // now: 102ms
    pLcd->setCursor(0, 0);
    pLcd->print("Twi ");
    lcdPrint(rNbrTwist);
    // pLcd->print("/");
    // lcdPrint(rNbrTwistLimit);
    pLcd->print("");
    lcdPrint(nNbrTwistSpeed);
    pLcd->print("r"); // rpm

    lcdPrint(dist_slider);
    pLcd->print("mm");


    pLcd->setCursor(0, 1);
    pLcd->print("Col ");
    lcdPrint(rNbrCollect);
    // pLcd->print("/");
    // lcdPrint(rNbrCollectLimit);
    pLcd->print("");
    lcdPrint(nNbrCollectSpeed);
    pLcd->print("r");

    lcdPrint(dist_slider_min);
    pLcd->print("mm");

    pLcd->setCursor(0, 2);
    pLcd->print("Spo ");
    lcdPrint(rNbrSpool);
    // pLcd->print("/");
    // lcdPrint(rNbrSpoolLimit);
    pLcd->print("");
    if( bAutomaticSpoolMode )
      lcdPrint( nAutomaticSpoolRotationSpeed );
    else
      lcdPrint( nNbrSpoolSpeed );
      
    pLcd->print("r");


    lcdPrint(dist_slider_max);
    pLcd->print("mm");

    if( 1 )
    {
      pLcd->setCursor(18, 3);
      if( bAutomaticSpoolMode )
      {
        pLcd->print("A");
      }
      else
      {
        pLcd->print("M");
      }
    }

    for(int i = 0; i < 4; ++i )
    {
      pLcd->setCursor(19, i);
      if(nNumLineEdited==i)
      {
        lcdPrintChar(127);
      }
      else
      {
        pLcd->print(" ");
      }
    }
    
  }

  ++nNbrFrame;
  // delay(10); // with 100ms of lcd refresh, no need to wait...
  countFps();
}

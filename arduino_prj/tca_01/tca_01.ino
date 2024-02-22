#define ENCODER_USE_INTERRUPTS // then really need to use pin compatible with interruption (cf my doc)
#include <Encoder.h> // by Paul Stoffregen

#define USE_HD44780

#ifndef USE_HD44780
  #if 0
    #include <LiquidCrystal_I2C.h>
  #else
    #include "LiquidCrystal_I2C_alma.h"
    // initialize the library with the numbers of the interface pins
    #define LiquidCrystal_I2C LiquidCrystal_I2C_Alma
  #endif
  LiquidCrystal_I2C lcd(0x27, 20, 4);
  

#else // USE_HD44780
  #include <Wire.h>
  #include <hd44780.h>
  #include <hd44780ioClass/hd44780_I2Cexp.h> // i2c LCD i/o class header
  hd44780_I2Cexp lcd;

#endif // USE_HD44780

#include "interpolator.hpp"

Encoder enc1(2,3);

#define PWM_TWIST      8
#define PHASE_TWIST   41

int bTwistDir = 1; // il y a une difference selon le sens du moteur !!!

MotorInterpolator mot1(PWM_TWIST,PHASE_TWIST);


#define enaPin 10 //enable-motor
#define dirPin 11 //direction
#define stepPin 12 //step-pulse

#define enaPin2 31 //enable-motor
#define dirPin2 33 //direction
#define stepPin2 35 //step-pulse

#define switchTwistGoPin 51 // button go +
#define switchTwistRevPin 53 // button go -

#define STPR 200 //steps-per-revolution


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
    Serial.print("fps: ");
    Serial.print(fps);
    Serial.print(", dt: ");
  #if 1
    {
      Serial.print(1000.f/fps,3);
      Serial.println("ms");
    }
#else
    {
      Serial.print(1000000.f/fps);
      Serial.println("micros");
    }
#endif

    fpsTimeStart = millis();
    fpsCpt = 0;
    //unsigned long durationprint = micros()-timeprintbegin;
    //Serial.print("duration fps micros: "); // 1228micros at 57600baud !!!, 1280 at 115200 (change nothing, it's more the time to compute)
    //Serial.println(durationprint);
  }

}

bool i2CAddrTest(uint8_t addr) {
  Wire.begin();
  Wire.beginTransmission(addr);
  if (Wire.endTransmission() == 0) {
    return true;
  }
  return false;
}

int bTwistGoButtonPushed = 1; // state of the button (so we detect it changes) // let's pretend it was on at startup as there's a spurious on this one
int bTwistRevButtonPushed = 1; // state of the button (so we detect it changes) // spurious here also now!
int nTwistMove = 0; // 0: stop, 1: positive direction, -1: reverse

void setup() 
{
  Serial.begin(57600);       // use the serial port // fast to not slowdown the program even with lot of trace
  Serial.println("setup starting...");

  pinMode(PWM_TWIST, OUTPUT);
  pinMode(PHASE_TWIST, OUTPUT);

  pinMode(enaPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);

  pinMode(enaPin2, OUTPUT);
  pinMode(dirPin2, OUTPUT);
  pinMode(stepPin2, OUTPUT);

  pinMode(switchTwistGoPin, INPUT);
  pinMode(switchTwistRevPin, INPUT);

  digitalWrite(enaPin ,LOW);
  digitalWrite(dirPin ,LOW);

#ifndef USE_HD44780
  if( i2CAddrTest(0x27) ) 
  {
    Serial.println("LCD: ok");
  }
  else
  {
    Serial.println("LCD: Alternate init on 0x3F");
    lcd = LiquidCrystal_I2C(0x3F, 20, 4);
  }
#else
  Wire.setClock( 400000UL); // change the i2c clock to 400kHz // more doesn't change anything
	int status = lcd.begin(20, 4);
	if(status) // non zero status means it was unsuccesful
  {
   Serial.println("ERR: LCD not ready"); 
  }
  else
  {
    lcd.print("Ready HD44780...");// Print a message to the LCD
  }
#endif
  lcd.init();                // initialize the lcd
  lcd.backlight();           // Turn on backlight // sans eclairage on voit rien...

  lcd.print("Ready...");// Print a message to the LCD

//  delay(2000); // for button to be ready (why go always trig once at startup?)
//  digitalRead(switchTwistGoPin); // permit to clear it !?!
  
  Serial.println("setup finished");

  unsigned long timeprintbegin = micros();
  Serial.println("BLABLALBALBLALBLABLABLA"); // 252micros at 115200
  unsigned long durationprint = micros()-timeprintbegin;
  Serial.print("durationprint blabla fps micros:"); // at 9600: 240micros, at 19200: 240micros, at 57600: 252micros, seems to be buffered ?
  Serial.println(durationprint);
}

unsigned long timeChange = millis();

const float rSecondToPrim = 31.2; // theorically 31 for fast motor // a bigger value count more turn than reality
void test10turn()
{
  int val1 = enc1.read();
  int val2 = 0;
  float rRev = val1/(rSecondToPrim*4.);
  float rTurnToDo = 10;

  

  if(0)
  {
    Serial.print("enc1: ");
    Serial.print(val1);
    Serial.print(", rev: ");
    Serial.println(rRev);
  }


  if( timeChange <= millis() || (rRev>0. && rRev>=rTurnToDo) || (rRev<0. && rRev<=-rTurnToDo) )
  {
    analogWrite(PWM_TWIST, 0);
    delay(500);

    if(1)
    {
      int val1 = enc1.read();
      float rRev = val1/(rSecondToPrim*4.);
      
      Serial.print("at stop: enc1: ");
      Serial.print(val1);
      Serial.print(", rev: ");
      Serial.println(rRev);
    }


    enc1.write(0);
    delay(500);

    timeChange = millis()+30000;
    analogWrite(PWM_TWIST, 25); // 25 => 10% // en dessous de 12 ca demarre pas toujours
    digitalWrite(PHASE_TWIST, bTwistDir);
    bTwistDir = !bTwistDir;
  }

  // delay(10);

  // quand on affiche la valeur a l'arret (on lit la meme erreur dans les 2 sens)

  // a pwm 25, avec une loop sans delay, on a 0.00 d'erreur entre la lecture et l'arret.
  // a pwm 25, avec une loop a 10, on a 0.00 d'erreur entre la lecture et l'arret
  // a pwm 25, avec une loop a 100, on a 0.02 d'erreur entre la lecture et l'arret
  
  // a pwm 255, avec une loop sans delay, on a 0.13 d'erreur entre la lecture et l'arret.
  // a pwm 255, avec une loop a 100, on a 0.70 d'erreur entre la lecture et l'arret, c'est assez constant.
}

void test3sec()
{
  analogWrite(PWM_TWIST, 200);
  delay(3*1000);
  analogWrite(PWM_TWIST, 0);
  delay(3*1000);
}

void asservTwist()
{
  if(!mot1.isMoving() && mot1.isArrived() )
  {
    /*
    delay(4000);
    if( mot1.getPos()<59 )  // start only 3 times
    {
      mot1.setNewGoal(mot1.getPos()+20,5);
    }
    */
    delay(3000);
    if( mot1.getPos()<59 )  // start only 1 time
    {
      mot1.setNewGoal(mot1.getPos()+990,1000); // was 1092
    }
  }
  float rMotRev1 = enc1.read()/(rSecondToPrim*4.);
  rMotRev1 = rMotRev1 * 40 / 12; // gear ratio
  // result is 5 times too much, why ?
  rMotRev1 /= 5;
  mot1.update(rMotRev1);
  lcd.home();
  //lcd.setCursor(0, 1);// set the cursor to column 0, line 1
  lcd.print("Rev: ");
  lcd.print(rMotRev1);
  lcd.print("  "); // clean remaining char when number are off
  delay(10);
}


void testStepper()
{
  digitalWrite( stepPin, HIGH ); // takes 6micros
  //delayMicroseconds(5);

  digitalWrite( stepPin,LOW );
  //delayMicroseconds(5);
}

void testStepperA4988()
{
  const int nNbrStepPerTurn = 200;
  const int nSleepMicroSec = 500;  // 500 was ok // 300 also for 17HE15-1504S without charge // with 314g charge, set 500

  for(int i = 0; i < nNbrStepPerTurn; ++i )
  {
    digitalWrite( stepPin2, HIGH ); // takes 6micros
    delayMicroseconds(nSleepMicroSec);

    digitalWrite( stepPin2,LOW );
    delayMicroseconds(nSleepMicroSec);
  }
  delay(2000);
}

void commandByButton()
{
  int pushed = digitalRead(switchTwistGoPin) == HIGH;
  if( bTwistGoButtonPushed != pushed )
  {
    bTwistGoButtonPushed = pushed;
    if(pushed)
    {
      Serial.println("button go pin pushed");
      if( nTwistMove == 1 ) 
      {
        nTwistMove = 0;
        mot1.brake();
      }
      else
      {
        nTwistMove = 1;
        mot1.setNewGoal(mot1.getPos()+1000,1000);
      }
    }
  }
  
  pushed = digitalRead(switchTwistRevPin) == HIGH;
  if( bTwistRevButtonPushed != pushed )
  {
    bTwistRevButtonPushed = pushed;
    if(pushed)
    {
      Serial.println("button rev pin pushed");
      if( nTwistMove == -1 ) 
      {
        nTwistMove = 0;
        mot1.brake();
      }
      else
      {
        nTwistMove = -1;
        mot1.setNewGoal(mot1.getPos()-1000,1000);
      }
    }
  }

  if(nTwistMove!=0 && mot1.getPos())
  {
    if(nTwistMove==1)
    {
      
    }
    else // if(nTwistMove==-1)
    {
      
    }
  }
    
  float rMotRev1 = enc1.read()/(rSecondToPrim*4.);
  rMotRev1 = rMotRev1 * 40 / 12; // gear ratio
  // result is 5 times too much, why ?
  rMotRev1 /= 5;
  mot1.update(rMotRev1);
  lcd.home();
  //lcd.setCursor(0, 1);// set the cursor to column 0, line 1
  lcd.print("Rev: ");
  lcd.print(rMotRev1);
  lcd.print(", twst: ");
  lcd.print(nTwistMove);
  lcd.print("  "); // clean remaining char when number are off
  delay(10);
}


long nNbrStepMotor1 = 0;
int bSendCmdMotor1 = 0;
int bFlipFlopMotor1 = 0;
void updateMachine1b()
{
  // the goal is to loop at 400microsec, so anytime we could decide to activate one motor or other motor or not
  const int target_frameduration_micros = 400;

  const int nNbrStepPerTurnMotor1 = 200;

  unsigned long framestart = micros();


  if(0)
  {
    digitalWrite( stepPin, HIGH ); // entre 4 et 8 micros
    digitalWrite( stepPin, LOW );
    int pushed = digitalRead(switchTwistGoPin) == HIGH; // entre 4 et 8 micros pour 2 lectures
    pushed = digitalRead(switchTwistRevPin) == HIGH;
  }
  
  int pushed = digitalRead(switchTwistGoPin) == HIGH;
  if( bTwistGoButtonPushed != pushed )
  {
    bTwistGoButtonPushed = pushed;
    if(pushed)
    {
      Serial.println("button go pin pushed");
      if( nTwistMove == 1 ) 
      {
        nTwistMove = 0;
        bSendCmdMotor1 = 0;
      }
      else
      {
        nTwistMove = 1;
        bSendCmdMotor1 = 1;
        digitalWrite(dirPin2,LOW);
      }
    }
  }
  
  pushed = digitalRead(switchTwistRevPin) == HIGH;
  if( bTwistRevButtonPushed != pushed )
  {
    bTwistRevButtonPushed = pushed;
    if(pushed)
    {
      Serial.println("button rev pin pushed");
      if( nTwistMove == -1 ) 
      {
        nTwistMove = 0;
        bSendCmdMotor1 = 0;
      }
      else
      {
        nTwistMove = -1;
        bSendCmdMotor1 = 1;
        digitalWrite(dirPin2,HIGH);
      }
    }
  }

  if(bSendCmdMotor1)
  {
    digitalWrite(stepPin2,bFlipFlopMotor1);
    bFlipFlopMotor1 = ! bFlipFlopMotor1;
    if(bFlipFlopMotor1)
    {
      nNbrStepMotor1 += nTwistMove;
    }
  }

  nNbrStepMotor1++; // just for debug lcd
    

  float rMotRev1 = nNbrStepMotor1 / (float)nNbrStepPerTurnMotor1;
  if(0)
  {
    if(0)
    {
      // the whole loop takes 34.2ms with liquid
      // the whole loop takes 30.0ms with liquid (Alma version)
      // the whole loop takes 20.0ms with hd44780
      // the whole loop takes 14.0ms with hd44780 and i2c clock at 400kHz

      lcd.home(); // 3.5ms !!! (without the alma lib)
      //lcd.setCursor(0, 1);// set the cursor to column 0, line 1 // 
      lcd.print("Rev: "); // 7.5ms!
      lcd.print(rMotRev1);
      lcd.print(", twst: ");
      lcd.print(nTwistMove);
      lcd.print("  "); // clean remaining char when number are off
    }
    else
    {
      // partial rendering:
      //
      // setcursor + one float takes 3.6ms with hd44780
      // setcursor + one float takes 3.1ms with hd44780 and i2c clock at 400kHz

      lcd.setCursor(5, 0);  // 1.5ms (Alma version) // 0.4ms with hd44780 and i2c clock at 400kHz
      //lcd.print(rMotRev1); // 5ms  (Alma version)
      
      //lcd.print("A"); // 1.5ms  (Alma version) // 0.4ms with hd44780 and i2c clock at 400kHz
      //lcd.print("ABCD"); // 5.6ms  (Alma version)
      //static char s[] = "A";
      //s[0] = 'A'+((nNbrStepMotor1/100)%26);
      //lcd.print(s); // 1.5ms  (Alma version)
    }
  }



  // maintain constant loop time

  unsigned long duration_micros = micros() - framestart;
  if( duration_micros < 1000000L ) // after 70min it loops, so it could become a very high number
  {
    unsigned long nTimeMiss = target_frameduration_micros - duration_micros;
    if( nTimeMiss < 1000000L ) // else overflow
    {
      delayMicroseconds( nTimeMiss-68 ); // the loop loose around 68ms for fps or system or ? (seems not to be fps printing, as a print every 15000 doesn't spare time)
      //Serial.print("DBG: margin (micros): ");
      //Serial.println(nTimeMiss);
    }
    else
    {
      if(1)
      {
        Serial.print("WRN: out of time frame (micros): ");
        Serial.println((signed long)((unsigned long)(-1)-nTimeMiss));
      }
    }
  }
}

void loop() 
{
 // Serial.println("loop...");

  //test10turn();
  //test3sec();
  //asservTwist();
  //commandByButton();

  //testStepper();
  //testStepperA4988();

  updateMachine1b();



  countFps();

  //delay(100);

}
#define ENCODER_USE_INTERRUPTS // then really need to use pin compatible with interruption (cf my doc)
#include <Encoder.h> // by Paul Stoffregen
#include <LiquidCrystal_I2C.h>
// initialize the library with the numbers of the interface pins
LiquidCrystal_I2C lcd(0x27, 20, 4);

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
    float fps = (float)(fpsCpt*1000)/diff;
    Serial.print("fps: ");
    Serial.print(fps);
    Serial.print(", dt: ");
    if(0)
    {
      Serial.print(1000.f/fps);
      Serial.println("ms");
    }
    else
    {
      Serial.print(1000000.f/fps);
      Serial.println("micros");
    }

    fpsTimeStart = millis();
    fpsCpt = 0;
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

  if( i2CAddrTest(0x27) ) 
  {
    Serial.println("LCD: ok");
  }
  else
  {
    Serial.println("LCD: Alternate init on 0x3F");
    lcd = LiquidCrystal_I2C(0x3F, 20, 4);
  }
  lcd.init();                // initialize the lcd
  lcd.backlight();           // Turn on backlight // sans eclairage on voit rien...

  lcd.print("Ready...");// Print a message to the LCD

//  delay(2000); // for button to be ready (why go always trig once at startup?)
//  digitalRead(switchTwistGoPin); // permit to clear it !?!
  
  Serial.println("setup finished");
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
  digitalWrite( stepPin2, HIGH ); // takes 6micros
  delayMicroseconds(500); // 500 was ok

  digitalWrite( stepPin2,LOW );
  delayMicroseconds(500); // 500 was ok
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

void loop() 
{
 // Serial.println("loop...");

  //test10turn();
  //test3sec();
  //asservTwist();
  //commandByButton();

  //testStepper();
  testStepperA4988();



  countFps();

  //delay(100);

}
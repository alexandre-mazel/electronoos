#define ENCODER_USE_INTERRUPTS // then really need to use pin compatible with interruption (cf my doc)
#include <Encoder.h> // by Paul Stoffregen

#include "interpolator.h"

Encoder enc1(2,3);

#define PWM_TWIST      8
#define PHASE_TWIST   41
int bTwistDir = 1; // il y a une difference selon le sens du moteur !!!

void setup() 
{
  Serial.begin(9600);       // use the serial port

  pinMode(PWM_TWIST, OUTPUT);
  pinMode(PHASE_TWIST, OUTPUT);
}

unsigned long timeChange = millis();

const float rSecondToPrim = 31.2; // theorically 31 for fast motor // a bigger value count more turn than reality
void loop() 
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
#define ENCODER_USE_INTERRUPTS // then really need to use pin compatible with interruption (cf my doc)

#include <Encoder.h> // by Paul Stoffregen

Encoder enc1(2,3);

#define PWM_TWIST      8
#define PHASE_TWIST   41
int bTwistDir = 1;

void setup() 
{
  Serial.begin(9600);       // use the serial port

  pinMode(PWM_TWIST, OUTPUT);
  pinMode(PHASE_TWIST, OUTPUT);
}

unsigned long timeChange = millis();

void loop() 
{
  int val1 = enc1.read();
  int val2 = 0;
  float rRev = val1/(31.*4);

  if( timeChange <= millis() || (rRev>0. && rRev>=2.) || (rRev<0. && rRev<=-2.) )
  {
    analogWrite(PWM_TWIST, 0);
    delay(500);
    enc1.write(0);

    timeChange = millis()+5000;
    analogWrite(PWM_TWIST, 25); // 25 => 10%
    digitalWrite(PHASE_TWIST, bTwistDir);
    bTwistDir = !bTwistDir;
  }

  Serial.print("enc1: ");
  Serial.print(val1);
  Serial.print(", rev: ");
  Serial.println(rRev);

  delay(100);
}
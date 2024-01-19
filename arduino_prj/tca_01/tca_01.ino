#include <Encoder.h> // by Paul Stoffregen

Encoder enc1(18,19);

#define PWM_TWIST      8
#define PHASE_TWIST   41
int bTwistDir = 1;

void setup() 
{
  Serial.begin(9600);       // use the serial port

  pinMode(PWM_TWIST, OUTPUT);
  pinMode(PHASE_TWIST, OUTPUT);
}

void loop() 
{
  int val = enc1.read();
  Serial.println("enc1: ");
  Serial.println(val);

  analogWrite(PWM_TWIST, 127); // 25 => 10%
  digitalWrite(PHASE_TWIST, bTwistDir);
  bTwistDir = !bTwistDir;

  delay(1000);


}
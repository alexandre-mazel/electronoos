// test a stepper motor on a pwm at 800mhz
// it doesn't works, the motor doesn't turn: perhaps we should look at the oscilloscope to measure the output is correct

#define enaPin2 31 //enable-motor
#define dirPin2 33 //direction
#define stepPin2 35 //step-pulse
#define stepPin2_pwm 44 //step-pulse on a 16bit pwm // can only be 44 45 or 46 for these methods



void setup() 
{
  Serial.begin(57600);
  pinMode(enaPin2, OUTPUT);
  pinMode(dirPin2, OUTPUT);
  pinMode(stepPin2, OUTPUT);

  digitalWrite(enaPin2,LOW);
  digitalWrite(dirPin2,LOW);

  Serial.println("test_torque_control_with_stepper");
}

void loop() 
{
  const int nNbrStepPerTurn = 200;
  const int nSleepMicroSec = 4000;  // 500 was ok // 300 also for 17HE15-1504S without charge // with 314g charge, set 500

  Serial.println("looping...");

  digitalWrite(enaPin2,LOW);
  for(int i = 0; i < nNbrStepPerTurn; ++i )
  {
    digitalWrite( stepPin2, HIGH ); // takes 6micros
    delayMicroseconds(nSleepMicroSec);

    digitalWrite( stepPin2,LOW );
    delayMicroseconds(nSleepMicroSec);
  }
  //digitalWrite(enaPin2,HIGH); // cut
  delay(2000);

}
// test a stepper motor on a pwm at 800mhz
// it doesn't works, the motor doesn't turn: perhaps we should look at the oscilloscope to measure the output is correct

#define enaPin2 31 //enable-motor
#define dirPin2 33 //direction
#define stepPin2 35 //step-pulse

#define switchTurbo 48



void setup() 
{
  Serial.begin(57600);
  pinMode(enaPin2, OUTPUT);
  pinMode(dirPin2, OUTPUT);
  pinMode(stepPin2, OUTPUT);

  pinMode(switchTurbo, INPUT);

  digitalWrite(enaPin2,LOW);
  digitalWrite(dirPin2,LOW);
  

  Serial.println("test_torque_control_with_stepper");
}

void slowGive()
{
  const int nNbrStepPerTurn = 200/20; // /20 to be more precise when putting turbo
  const int nSleepMicroSec = 12000;  // 500 was ok // 300 also for 17HE15-1504S without charge // with 314g charge, set 500 // max 16383
  const int nNbrMulti = 5;

  Serial.println("looping...");

  digitalWrite(dirPin2,HIGH);

  digitalWrite(enaPin2,LOW);
  for(int i = 0; i < nNbrStepPerTurn; ++i )
  {
    digitalWrite( stepPin2, HIGH ); // takes 6micros
    for(int j = 0; j < nNbrMulti; ++j)
      delayMicroseconds(nSleepMicroSec);

    digitalWrite( stepPin2,LOW );
    for(int j = 0; j < nNbrMulti; ++j)
      delayMicroseconds(nSleepMicroSec);
  }
  //digitalWrite(enaPin2,HIGH); // cut
  //delay(2000);
}

void turboGive()
{
  const int nNbrStepPerTurn = 200;
  const int nSleepMicroSec = 3000;  // 500 was ok // 300 also for 17HE15-1504S without charge // with 314g charge, set 500 // max 16383
  const int nNbrMulti = 1;

  Serial.println("looping...");

  digitalWrite(dirPin2,HIGH);

  digitalWrite(enaPin2,LOW);
  for(int i = 0; i < nNbrStepPerTurn; ++i )
  {
    digitalWrite( stepPin2, HIGH ); // takes 6micros
    for(int j = 0; j < nNbrMulti; ++j)
      delayMicroseconds(nSleepMicroSec);

    digitalWrite( stepPin2,LOW );
    for(int j = 0; j < nNbrMulti; ++j)
      delayMicroseconds(nSleepMicroSec);
  }
  //digitalWrite(enaPin2,HIGH); // cut
  //delay(2000);
}

void fastRoll()
{
  // fast in the other direction
  const int nNbrStepPerTurn = 200;
  const int nSleepMicroSec = 500;  // 500 was ok // 300 also for 17HE15-1504S without charge // with 314g charge, set 500 // max 16383

  Serial.println("looping...");

  digitalWrite(dirPin2,LOW);
  digitalWrite(enaPin2,LOW);
  for(int i = 0; i < nNbrStepPerTurn; ++i )
  {
    digitalWrite( stepPin2, HIGH ); // takes 6micros
    delayMicroseconds(nSleepMicroSec);

    digitalWrite( stepPin2,LOW );
    delayMicroseconds(nSleepMicroSec);
  }
  //digitalWrite(enaPin2,HIGH); // cut
  //delay(2000);
}

void loop() 
{
  if(0)
  {
    fastRoll(); // to create the spool
  }
  else
  {
    int bTurbo = digitalRead(switchTurbo) == HIGH;
    Serial.print("DBG: bTurbo: "); Serial.println(bTurbo); 
    if(bTurbo)
      turboGive();
    else
      slowGive();
  }
  


  
}
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
  pinMode(stepPin2_pwm, OUTPUT);

  digitalWrite(enaPin2,LOW);
  digitalWrite(dirPin2,LOW);

  
  //initPWM(800,0);
  //initPWM(200,0); // try slower (not working also)

  // works fine when use with a normal analogWrite
  //initPWM(1200,0);  // 1200 gives a period of 833us
  initPWM(1333,0);  // 1333 gives a period of 750us
  initPWM(2500,0); // 2500 gives a period of 400us
}

void loop() {
  Serial.println("test_custom_pwm");
  const int nNbrStepPerTurn = 200;
  //const unsigned long nTimeOneTurnMicroSec = 1000L*nNbrStepPerTurn;
  const int nTimeOneTurnMs = (1000/(2500./2))*nNbrStepPerTurn; // add a bit for a full turn

  digitalWrite(enaPin2,LOW); // enable

  analogWrite( stepPin2_pwm, 255/2. ); // this is working (at 490Hz) (but don't call initPWM before)

  //setPWMDutyCycle8Bit(44,128);
  //setPWMDutyCycle8Bit(45,64);
  //setPWMDutyCycle8Bit(46,192);
  //setPWMDutyCycle8Bit(stepPin2_pwm,128); // doesn't works but the analogWrite is working using the freq set initially!

  delay(nTimeOneTurnMs);

  disablePWMOutput(stepPin2_pwm);
  digitalWrite(enaPin2,HIGH); // disable
  
  delay(2000);

}

void initPWM(unsigned long freq,byte rampmode) {
  //calculate TOP
  unsigned long clockspercycle = (F_CPU/freq);
  Serial.print("initPWM: clockspercycle: ");Serial.println(clockspercycle);
  if (rampmode) { //dual slope mode requested
    clockspercycle=clockspercycle>>1;
  }
  byte presc = 1; //this is the value to be written to the CS bits, NOT the actual prescaler
  while (clockspercycle>65536) { //do we need to prescale? 
    presc++; //increase prescaling
    clockspercycle=clockspercycle>>(presc>3?2:3); //divide required top by 8 or 4
    //no test needed for whether we've exhausted available prescalers, because 20,000,000/1024 will fit in 16-bits, and that's the highest rated speed for classic AVRs
  }
  Serial.print("initPWM: presc: ");Serial.println(presc);
  // reset registers
  TCCR5B=0; 
  TCCR5A=0; 
  byte wgm = (rampmode?(rampmode==1?10:8):14); //determine desired WGM
  Serial.print("initPWM: wgm: ");Serial.println(wgm);
  ICR5 = clockspercycle-1;
  //clear these for good measure
  OCR5A=0;
  OCR5B=0;
  OCR5C=0;
  TCCR5A=0x03&wgm; //set low bits of WGM 
  TCCR5B=((wgm<<3)&0x18)|presc; //set rest of WGM, prescaler and start timer
}

//8-bit resolution, like analogWrite()
void setPWMDutyCycle8Bit(byte pin,byte dutycycle) {
  unsigned int ocrval=map(dutycycle,0,255,0,ICR5);
  if (!(pin==44||pin==45||pin==46)) { //if we call on a pin that isn't on this timer, return immediately.
    return; 
  }
  switch (pin)
  {
    case 46:
      OCR5A=ocrval;
      TCCR5A|=0x80; //COMA=2 non-inverting pwm
      break;
    case 45:
      OCR5B=ocrval;
      TCCR5A|=0x20; //COMA=2 non-inverting pwm
      break;
    case 44:
      OCR5B=ocrval;
      TCCR5A|=0x08; //COMA=2 non-inverting pwm
      break;
  }
  pinMode(pin,OUTPUT);
}

void disablePWMOutput(byte pin) {
  if (!(pin==44||pin==45||pin==46)) { //if we call on a pin that isn't on this timer, return immediately.
    return; 
  }
  switch (pin)
  {
    case 46:
      TCCR5A&=0x3F; //COMA=0 off
      break;
    case 45:
      TCCR5A&=0xCF; //COMA=0 off
      break;
    case 44:
      TCCR5A&=0xF3; //COMA=0 off
      break;
  }
  pinMode(pin,INPUT); //This may not be the ideal behavior for your use case - possibly digitalWrite'ing it LOW would be better.
}

/* 
// uncomment and fill in MAX to get a high-res version where duty cycle expressed as 0~MAX
void setDutyCycleHiRes(byte pin,unsigned int dutycycle) {
  unsigned int ocrval=map(dutycycle,0,MAX,0,ICR5)
  if (!(pin==44||pin==45||pin==46)) { //if we call on a pin that isn't on this timer, return immediately.
    return; 
  }
  switch (pin)
  {
    case 46:
      OCR5A=ocrval;
      TCCR5A|=0x80; //COMA=2 non-inverting pwm
      break;
    case 45:
      OCR5B=ocrval;
      TCCR5B|=0x80; //COMA=2 non-inverting pwm
      break;
    case 44:
      OCR5C=ocrval;
      TCCR5C|=0x80; //COMA=2 non-inverting pwm
      break;
  }
  pinMode(pin,OUTPUT);
}
*/
#define enaPin1   48  // enable-motor
#define dirPin1   49  // direction
#define stepPin1  50  // step-pulse

void setup()
{
  Serial.begin( 115200 );

  pinMode( enaPin1, OUTPUT );
  pinMode( dirPin1, OUTPUT );
  pinMode( stepPin1, OUTPUT );


  digitalWrite( enaPin1,LOW );
  digitalWrite( dirPin1,LOW );
}

void testOneTurn(int bEnableThenDisable = 0)
{
  const int nNbrStepPerTurn = 200;
  const int nSleepMicroSec = 550;  // 500 was ok // 300 also for 17HE15-1504S without charge // with 314g charge, set 500

  if( bEnableThenDisable ) 
  {
    digitalWrite( enaPin1,LOW );
    delay(8); // Time for ena to be taken into account ?
  }
  
  for(int i = 0; i < nNbrStepPerTurn; ++i )
  {
    digitalWrite( stepPin1, HIGH ); // takes 6micros
    delayMicroseconds(nSleepMicroSec);

    digitalWrite( stepPin1,LOW );
    delayMicroseconds(nSleepMicroSec);
  }
  if(bEnableThenDisable) digitalWrite( enaPin1, HIGH ); // disable
}

void loop() 
{
  testOneTurn(1);
  delay(2000);

  digitalWrite( enaPin1,LOW );
  delay(8);
  for(int i = 0; i < 20; ++i )
  {
    testOneTurn();
  }
  delay(2000);
}
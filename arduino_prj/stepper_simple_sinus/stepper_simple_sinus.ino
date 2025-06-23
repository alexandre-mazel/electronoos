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

void turnOneTurn( int bEnableThenDisable = 0 )
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
} // turnOneTurn

void turnAccelDeccel( float rNbrOfTurn, float rRpm, int bEnableThenDisable = 0 )
{
  // turn a number of turn atteigning a speed target after ramping
  // Interest: permit to attein higher speed than when setting them directly to max speed
  //
  // - rNbrOfTurn: number of turn to perform in total (including ramping)
  // - rRpm: max speed to attein (max 440 with a light load with the 17HE15-1504S)
  // - bEnableThenDisable: when set: handle the enabling (stiffnessing) of the motor
  // 
  // 
  const unsigned int nNbrStepPerTurn = 200; // 200 for the 17HE15-1504S
  const unsigned int nTimeHalfPeriodStart = 10000; // put here a big value to start slow // too big is not slower (max is 16383)
  unsigned int nTimeHalfPeriodTarget =  (60*1000000L /rRpm) /  ( nNbrStepPerTurn* 2 );

  unsigned int nTimeHalfPeriod = nTimeHalfPeriodStart;

  Serial.print( "DBG: turnAccelDeccel: nTimeHalfPeriodTarget:" ); Serial.println( nTimeHalfPeriodTarget );

  float rCurrentNbrOfTurn = 0; // an approximative number of turn (float error that adds)
  int nEntireNbrOfTurn = 0; // precise number of turn, but count entire turn

  int nNbrStep = 0;
  float rIncPerStep = 1.f/nNbrStepPerTurn; // not precise but will be corrected after each entire turn

  if( bEnableThenDisable ) 
  {
    digitalWrite( enaPin1,LOW );
    delay(8); // Time for ena to be taken into account ?
  }

  while( rCurrentNbrOfTurn < rNbrOfTurn )
  {
    digitalWrite( stepPin1, HIGH ); // takes 6micros
    delayMicroseconds(nTimeHalfPeriod);

    digitalWrite( stepPin1,LOW );
    delayMicroseconds(nTimeHalfPeriod);

    if( nTimeHalfPeriod > nTimeHalfPeriodTarget+100 )
    {
      nTimeHalfPeriod -= 100;
      
    }
    else if( nTimeHalfPeriod > nTimeHalfPeriodTarget && (nNbrStep & 0x3F) == 0x3F )
    {
      nTimeHalfPeriod -= 1;
    }
    //Serial.print( "DBG: turnAccelDeccel: nTimeHalfPeriod:" ); Serial.println( nTimeHalfPeriod );

    ++nNbrStep;
    if( nNbrStep == nNbrStepPerTurn )
    {
      nNbrStep = 0;
      ++nEntireNbrOfTurn;
      rCurrentNbrOfTurn = nEntireNbrOfTurn;
    }
    else
    {
      rCurrentNbrOfTurn += rIncPerStep;
    }
  }


  if(bEnableThenDisable) digitalWrite( enaPin1, HIGH ); // disable
} // turnOneTurn

void loop() 
{
  Serial.println("Loop begin");

  if( 0 )
  {
    turnOneTurn(1);
    delay(2000);
  }

  /*

  digitalWrite( enaPin1,LOW );
  delay(12);
  for(int i = 0; i < 20; ++i )
  {
    turnOneTurn();
  }
  delay(2000);

  */

  if( 1 )
  {
      turnAccelDeccel( 5,60,1 );
      delay(2000);
  }

  turnAccelDeccel( 60,450,1 );
  delay(2000);

}
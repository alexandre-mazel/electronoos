#include "interpolator.h"
#include <Arduino.h>

#define myAssert(val) {if(!(val)){Serial.print("ASSERT FAILED at ");Serial.print(__FILE__);Serial.print(": ");Serial.println(__LINE__);delay(2000);}}
#define myAssertDiff(val,ref) {if( abs((val)-(ref)) > 0.1) {Serial.print("ASSERT FAILED: ");Serial.print(val);Serial.print(" != ");Serial.print(ref);Serial.print(" at ");Serial.print(__FILE__);Serial.print(": ");Serial.println(__LINE__);delay(2000);}}

#define DEBUG

// #define CLEAN_DESTROY // define me if on a system where there's a life after this program, undefined to gain code size

float gaussian(float x)
{
    // inspired by  https://codepen.io/zapplebee/pen/ByvmMo
    // returns values along a bell curve from 0 - 1 - 0 with an input of 0 - 1.
    const float stdD = .125;
    const float mean = .5;
    const float pi = 3.141592653589793f;
    const float e =  2.71828f;

    //float midpoint = 1 / (( 1/( stdD * sqrt(2 * pi) ) ) * pow(e , -1 * sq(0.5 - mean) / (2 * sq(stdD))));
    const float midpoint = 0.31332853432887503;

    //Serial.print("midpoint: "); Serial.println( midpoint );
    //Serial.print("-1 * sq(x - mean): "); Serial.println( -1 * sq(x - mean) );

    // float ret = (( 1/( stdD * sqrt(2 * pi) ) ) * pow(e , -1 * sq(x - mean) / (2 * sq(stdD)))) * midpoint;

    // precalcFirst = 1/( stdD * np.sqrt(2 * pi) )
    const float precalcFirst = 3.1915382432114616;
    // precalcSecond = 2 * sq(stdD)
    const float precalcSecond = 0.03125;

    float ret = (( precalcFirst ) * pow(e , -1 * sq(x - mean) / (precalcSecond))) * midpoint;

    //Serial.print( "x: " );
    //Serial.print( x, 4 );
    //Serial.print( ", gaussian: " );
    //Serial.println( ret, 10 );
    return ret;
}

Interpolator::Interpolator()
    : bIsFinished_( true )
    , rPos_( 0.f )
    , rStartPos_( 0.f )
    , rGoalPos_( 0.f )
    , rStartTime_( 0 )
    , rGoalTime_( 0 )
    , bPingPong_( false )
    , bSpline_( false )
{
}

        
float Interpolator:: update( timetype current_time_ms )
{
   if( current_time_ms >= rGoalTime_ )
    {
        rPos_ = rGoalPos_;
        if( bPingPong_ )
        {
            float current = rGoalPos_;
            rGoalPos_ = rStartPos_;
            rStartPos_ = current;
            timetype end_time = rGoalTime_;
            rGoalTime_ = rGoalTime_ + ( rGoalTime_ - rStartTime_ );
            rStartTime_ = end_time;
            return false;
        }
        bIsFinished_ = true;
        return true;
    }
    float val = 0;
    float rt = ( current_time_ms - rStartTime_ ) / (float)( rGoalTime_ - rStartTime_ );
    float delta = ( rGoalPos_ - rStartPos_ );
    
    if( ! bSpline_ )
    {
        val = rStartPos_ + delta*rt;
    }
    else
    {        
        val = delta * gaussian(rt/2);
        val = rStartPos_ + val;
    }

    rPos_ = val;

    if(1)
    {
      Serial.print("DBG: Interpolator::update: this: "); Serial.println( (int)(this) );
      Serial.print("DBG: Interpolator::update: rt: "); Serial.println( rt );
      Serial.print("DBG: Interpolator::update: delta: "); Serial.println( delta );
      Serial.print("DBG: Interpolator::update: val: "); Serial.println( val );
    }
    
    return false;  
}

void Interpolator::setRelGoal( float rGoalPos, timetype tGoalRel )
{
    setAbsGoal( rGoalPos + rPos_, tGoalRel );
}

void Interpolator::setAbsGoal( float rGoalPos, timetype tGoalRel )
{
    rStartPos_      = rPos_;
    rGoalPos_       = rGoalPos;
    rStartTime_    = millis(); // ugly to use millis here (not platform dependant)
    rGoalTime_     = rStartTime_ + tGoalRel;
    bIsFinished_   = false;
    bPingPong_     = false;
    bSpline_       = false;
}

void Interpolator::print()
{
    Serial.println("DBG: Interpolator:");
    Serial.print("bIsFinished_: "); Serial.println( bIsFinished_ );
    Serial.print("rPos_: "); Serial.println( rPos_ );
    Serial.print("rStartPos_: "); Serial.println( rStartPos_ );
    Serial.print("rGoalPos_: "); Serial.println( rGoalPos_ );
    Serial.print("rStartTime_: "); Serial.println( rStartTime_ );
    Serial.print("rGoalTime_: "); Serial.println( rGoalTime_ );
    Serial.print("bPingPong_: "); Serial.println( bPingPong_ );
    Serial.print("bSpline_: "); Serial.println( bSpline_ );
}


void Interpolator::autoTest()
{
    Serial.println("DBG: Interpolator::autoTest");
    
    myAssert(1==1); // test myAssert :)
    // myAssert(0); // test myAssert :)
    
    Interpolator int1;
    
    const int timeGoal1 = 500;
    int1.setRelGoal( 10,timeGoal1 );
    long int timeBegin = millis();
    pinMode(LED_BUILTIN, OUTPUT);
    int1.update(millis());
    delay(10);
    myAssertDiff(int1.getVal(), 0);
    while( ! int1.isFinished() )
    {
        int1.update(millis());
        analogWrite(LED_BUILTIN, int1.getVal()*25); // sur le R3, c'est la led la plus a coté du pin 13
        //int1.print();
        delay(10);
    }
    long int duration = millis()-timeBegin;
    myAssert(millis()-timeBegin > timeGoal1-50);
    myAssert(millis()-timeBegin < timeGoal1+50);
    myAssertDiff(int1.getVal(), 10);

    if(1)
    {
      const int timeGoal1 = 1000;
      int1.setRelGoal( -9,timeGoal1 ); // previously finished at 10
      int1.setSpline( true );
      long int timeBegin = millis();
      pinMode(LED_BUILTIN, OUTPUT);
      int1.update(millis());
      myAssertDiff(int1.getVal(), 10);
      while( ! int1.isFinished() )
      {
          int1.update(millis());
          analogWrite(LED_BUILTIN, int1.getVal()*25); // sur le R3, c'est la led la plus a coté du pin 13
          //int1.print();
          delay(10);
      }
      long int duration = millis()-timeBegin;
      myAssert(millis()-timeBegin > timeGoal1-50);
      myAssert(millis()-timeBegin < timeGoal1+50);
      myAssertDiff(int1.getVal(), 1);
    }
    
    if(0)
    {
      // locate LED_BUILTIN position on the board
      for(int i = 0; i < 10; ++i )
      {
          digitalWrite(LED_BUILTIN, HIGH);
          delay(1000);
          digitalWrite(LED_BUILTIN, LOW);
          delay(1000);
      }
    }

    if(0)
    {
        // test gaussian
        for( int i = 0; i < 100; ++i )
        {
          float x = i / 100.f;
          float y = gaussian(x);
        }
        
        for( int i = 0; i < 5; ++i )
        {
          gaussian( i*0.125 );
        }

        Serial.println("gaussian speed test...");
        float y;
        long int timeBegin = millis();
        for( long int i = 0; i < 10000; ++i )
        {
          y = gaussian(i);
          if( y < -1 ) Serial.print("cette ligne sert a enlever l'optimisation du compiler sur du code inutile (eg l'appal a la fonction gaussian si on n'utilise pas la valeur de retour)");
        }
        long int duration = millis() - timeBegin; 
        Serial.print("duration 10000 gaussian (ms): "); // Mega2560: 2.090s it's the same after const optimisation: the compiler has already optimise consts. Kudos !
        Serial.println(duration);
        delay(100000);
    }

    if(1)
     {   
        for( int spline = 0; spline < 2; ++spline )
        {
            const int timeGoal1 = 2000;
            int1.forcePos( 0 );
            int1.setRelGoal( 1, timeGoal1 );
            int1.setPingpong(true);
            int1.setSpline(spline);
            long int timeBegin = millis();
            pinMode(LED_BUILTIN, OUTPUT);
            while( millis()-timeBegin < 10000 )
            {
                int1.update(millis());
                analogWrite(LED_BUILTIN, int1.getVal()*255);
                //int1.print();
                delay(100);
            }
        }
    }
    
    
    Serial.println("DBG: Interpolator::autoTest: success");
}

InterpolatorManager::InterpolatorManager()
  : pInterpolators_  ( NULL )
  , nNbrInterpolator_( 0 )
{
}

void InterpolatorManager::init( int nNbrInterpolator )
{
  nNbrInterpolator_ = nNbrInterpolator;
  //pInterpolators = (Interpolator*)malloc(sizeof(Interpolator)*nNbrInterpolator_); // C syntaxe
  pInterpolators_ = new Interpolator[nNbrInterpolator_];
}

InterpolatorManager::~InterpolatorManager()
{
#ifdef CLEAN_DESTROY
  // free(pInterpolators_); // C syntaxe
  delete pInterpolators_[];

  pInterpolators_ = NULL;
  nNbrInterpolator_ = 0;
#endif // CLEAN_DESTROY
}

InterpolatorManager::update(timetype current_time_ms)
{
  Interpolator* p =  pInterpolators_;
  Interpolator* pEnd =  pInterpolators_ + nNbrInterpolator_;
  while( p != pEnd )
  {
    p->update( current_time_ms );
    ++p;
  }
}

InterpolatorManager interpolatorManager;

#include "interpolator.h"
#include <Arduino.h>

#define myAssert(val) {if(!val){Serial.print("ASSERT FAILED: ");Serial.print(__FILE__);Serial.print(": ");Serial.println(__LINE__);delay(2000);}}

#define DEBUG

float gaussian(float x)
{
    // from https://codepen.io/zapplebee/pen/ByvmMo
    const float stdD = .125;
    const float mean = .5;
    const float pi = 3.141592653589793f;
    const float e =  2.71828f;

    float midpoint = 1 / (( 1/( stdD * sqrt(2 * pi) ) ) * pow(e , -1 * sq(x - mean) / (2 * sq(stdD))));

    return (( 1/( stdD * sqrt(2 * pi) ) ) * pow(e , -1 * sq(x - mean) / (2 * sq(stdD)))) * midpoint;
}

Interpolator::Interpolator()
    : bIsFinished_( true )
    , rPos_( 0.f )
    , rStartPos_( 0.f )
    , rGoalPos_( 0.f )
    , rStartTime_( 0 )
    , rGoalTime_( 0 )
{
}

        
float Interpolator:: update( timeunit time_ms )
{
    
}

void Interpolator::setRelGoal( float rGoalPos, timeunit tGoalRel )
{
    setAbsGoal( rGoalPos + rPos_, tGoalRel );
}

void Interpolator::setAbsGoal( float rGoalPos, timeunit tGoalRel )
{
    rStartPos_      = rPos_;
    rGoalPos_       = rGoalPos;
    rStartTime_    = millis(); // ugly to use millis here (not platform dependant)
    rGoalTime_     = rStartTime_ + tGoalRel;
    bIsFinished_   = false;
}

void Interpolator::print()
{
    Serial.println("DBG: Interpolator:");
    Serial.print("bIsFinished_: "); Serial.println( bIsFinished_ );
    Serial.print("rPos_: "); Serial.println( rPos_ );
    Serial.print("rStartPos_: "); Serial.println( rStartPos_ );
    Serial.print("rGoalPos_: "); Serial.println( rGoalPos_ );
    Serial.print("rStartTime_: "); Serial.println( rStartTime_ );
    Serial.print("rStartTime_: "); Serial.println( rStartTime_ );
}


void Interpolator::autoTest()
{
    Serial.println("DBG: Interpolator::autoTest");
    
    myAssert(1); // test myAssert :)
    myAssert(0); // test myAssert :)
    
    Interpolator int1;
    
    const int timeGoal1 = 500;
    int1.setRelGoal(1,timeGoal1);
    long int timeBegin = millis();
    while(!int1.isFinished())
    {
        int1.print();
        delay(10);
    }
    myAssert(millis()-timeBegin > timeGoal1-50);
    myAssert(millis()-timeBegin < timeGoal1+50);
    
    
    Serial.println("DBG: Interpolator::autoTest: success");
}
#include "interpolator.hpp"

#include <Arduino.h>

#define sq(x) ( (x)*(x) )
#define pow(x,y) ((x)+(y)) // TODO
#define sqrt(x) (x) // TODO


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


MotorInterpolator::MotorInterpolator( int nSpeedPin, int nReversePin )
{
    nSpeedPin_ = nSpeedPin;
    nReversePin_ = nReversePin;
    nLastPwm_ = 0;
    this->stop();
}

int MotorInterpolator::setNewGoal( float rNewGoal, float rTimeSec )
{
  Serial.print("INF: setNewGoal: ");
  Serial.print(rNewGoal);
  Serial.print(", rTimeSec: ");
  Serial.println(rTimeSec);
  rGoal_ = rNewGoal;
  if(rTimeSec < 0.1)
  {
    rTimeSec = 0.1;
  }
  nTimeStartMove_ = millis();
  rGoalTimeMs_ = nTimeStartMove_+rTimeSec*1000;
}

bool MotorInterpolator::stop()
{
    rGoal_ = 0;
    rGoalTimeMs_ = millis();
    rLastPos_ = rGoal_;
    _sendPwm(0);
}

bool MotorInterpolator::update(float rCurrentRev)
{
  int nNewPwm = 0;
  const int rTurnToBrake = 2.f;
  const int rTimeToAccelerate = 2.f;
  if( rCurrentRev < rGoal_ - rTurnToBrake )
  {
    // acceleration or full throttle
    if(millis()-nTimeStartMove_ < rTimeToAccelerate)
    {
      // accelerate
      nNewPwm = (int) ( ((millis()-nTimeStartMove_)*255) / rTimeToAccelerate);
      if( nNewPwm > 255) nNewPwm = 255;
    }
    else
    {
      nNewPwm = 255;
    }

  }
  else if( rCurrentRev < rGoal_ )
  {
    // slowing
    nNewPwm = (int)( ((rGoal_ - rCurrentRev)*255)/rTurnToBrake );
  }

  if( nLastPwm_ != nNewPwm )
  {
    nLastPwm_ = nNewPwm;
    analogWrite(nSpeedPin_, nLastPwm_);
  }
  Serial.print("INF: update: rev: ");
  Serial.print(rCurrentRev);
  Serial.print(", goal: ");
  Serial.print(rGoal_);
  Serial.print(", nTimeStartMove_: ");
  Serial.print(nTimeStartMove_);
  Serial.print(", rGoalTimeMs_: ");
  Serial.print(rGoalTimeMs_);
  Serial.print(", nNewPwm: ");
  Serial.println(nNewPwm);
}

void MotorInterpolator::_sendPwm( uint8 nVal )
{
    analogWrite(nSpeedPin_, nVal);
}

void MotorInterpolator::_sendReverse( bool bReverse )
{
    analogWrite(nReversePin_, bReverse?1:0);
}

bool MotorInterpolator::isArrived(void) 
{
  return abs(rGoal_-rLastPos_)<0.02;
}

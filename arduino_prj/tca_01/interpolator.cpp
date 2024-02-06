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
    rLastPos_ = 0.f;
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
  bIsInBrake_ = false;
  nTimeSinceMotorNotMovingAndPwm_ = millis();

  _sendReverse(rGoal_<rLastPos_);
}

bool MotorInterpolator::stop()
{
  Serial.println("INF: stop");
  rGoalTimeMs_ = millis();
  rGoal_ = rLastPos_;
  nLastPwm_ = 0;
  bIsInBrake_ = false;

  _sendPwm(0);
}
bool MotorInterpolator::brake()
{
  
  const float rRotToBrake = 0.5;

  if(bIsInBrake_)
  {
    return;
  }

  Serial.println("INF: brake");

  if( nLastPwm_ == 0 || abs(rGoal_ - rLastPos_) < rRotToBrake / 3 )
  {
    stop();
    return;
  }
  // was moving
  bIsInBrake_ = true;
  if( abs(rGoal_ - rLastPos_) < rRotToBrake )
  {
    // nothing to do
    return;
  }
  if( rGoal_ > rLastPos_ )
  {
    rGoal_ = rLastPos_ + rRotToBrake;
  }
  else
  {
    rGoal_ = rLastPos_ - rRotToBrake;
  }
}

bool MotorInterpolator::update(float rCurrentRev)
{
  if (this->isArrived() && ! this->isMoving()) // need to update even if arrived if still moving (just send a pwm=0)
  {
    return;
  }
  int nNewPwm = 0;
  const int rTurnToBrake = 5.f;
  const int rTimeToAccelerateSec = 2.f;
  const int rThreshold = 0.1;
  //int nMaxSpeed = 
  if( abs(rCurrentRev - rGoal_) > rTurnToBrake )
  {

    // acceleration or full throttle
    if(millis()-nTimeStartMove_ < rTimeToAccelerateSec*1000)
    {
      // accelerate
      nNewPwm = (int) ( ((millis()-nTimeStartMove_)*255) / (rTimeToAccelerateSec*1000));
      if( nNewPwm > 255) nNewPwm = 255;
    }
    else
    {
      nNewPwm = 255;
    }

  }
  //else if( rCurrentRev < rGoal_ - rThreshold )
  else if( abs(rCurrentRev - rGoal_) > rThreshold )
  {
    // slowing
    nNewPwm = (int)( (abs(rGoal_ - rCurrentRev)*255)/rTurnToBrake );
    if(nNewPwm < 12) nNewPwm = 12; // need to continue to turn but at lower than 30 it stops
  }
  else
  {
    // arrived !
    Serial.println("INF: update: Arrived !");
    nNewPwm = 0;
  }

  if( nNewPwm < 10) nNewPwm = 0; // prevent sending nearly 0

  if( nLastPwm_ != nNewPwm )
  {
    if( bIsInBrake_ && nNewPwm > nLastPwm_ )
    {
      Serial.println("INF: update: in brake and depassed, stopping !");
      stop();
      return;
    }
    nLastPwm_ = nNewPwm;
    analogWrite(nSpeedPin_, nLastPwm_);
  }
  Serial.print("INF: update: time: ");
  Serial.print(millis());
  Serial.print(", rev: ");
  Serial.print(rCurrentRev);
  Serial.print(", goal: ");
  Serial.print(rGoal_);
  Serial.print(", nTimeStartMove_: ");
  Serial.print(nTimeStartMove_);
  Serial.print(", rGoalTimeMs_: ");
  Serial.print(rGoalTimeMs_);
  Serial.print(", nNewPwm: ");
  Serial.println(nNewPwm);

  if(rLastPos_ != rCurrentRev )
  {
    rLastPos_ = rCurrentRev;
    nTimeSinceMotorNotMovingAndPwm_ = millis();
  }
  else
  {
    // not moving
    if(nLastPwm_ > 0 && millis()-nTimeSinceMotorNotMovingAndPwm_> 3000 )
    {
      Serial.println("INF: update: looks stalled, stopping...");
      stop(); // stop forcing !
      return;
    }
  }
  if( nNewPwm == 0 && 
        ( 
            ( abs(rCurrentRev-rGoal_) < 0.4 && millis()-nTimeStartMove_ > 1000 )
            || ( abs(rCurrentRev-rGoal_) < 1. && millis()-nTimeStartMove_ > 5000 )
        )
  )

  {
    // we will never reach the target, let's says the move is finished
    rGoal_ = rLastPos_;
  }
}

void MotorInterpolator::_sendPwm( uint8 nVal )
{
    analogWrite(nSpeedPin_, nVal);
}

void MotorInterpolator::_sendReverse( bool bReverse )
{
    digitalWrite(nReversePin_, bReverse?HIGH:LOW);
}

bool MotorInterpolator::isArrived(void) 
{
  return abs(rGoal_-rLastPos_) < 0.1;
}

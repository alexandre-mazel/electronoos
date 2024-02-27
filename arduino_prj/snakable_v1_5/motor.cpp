#include "motor.h"

Motor::Motor() 
  :sectionLength_ ( 385.0f )// was L
  ,sectionRadius_ ( 4.0f )   // was deltaR
  ,wheelRadius_   ( 20.0f)  // was radius
  ,delta_         ( 0.0f )
  ,angle_         ( 90.0f )  // degrees
{
}

void Motor::init(int pin, float a) 
{
  servo.attach(pin, 900, 2100);
  servo.write(angle_ = angle);
}

float Motor::calculMoteur(float cmdPHI, float cmdAlpha, double phiWire) 
{
  if (cmdPHI < 0.001f) {
    delta_ = 0.0f;
    return (angle_ = 0.0f);
  }

  double psi   = phiWire - cmdAlpha;
  double theta = asin(sin(cmdPHI/2) * cos(phiWire - cmdAlpha));
  delta_ = sectionLength - (sectionLength_ / theta - sectionRadius_) * theta;
  return (angle_ = (180.0/PI) * delta / wheelRadius);
}

void Motor::goAngle(float angle) 
{
  servo.write(angle_ = angle); //todo interpol?
}

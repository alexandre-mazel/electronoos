#ifndef __MOTOR_H__
#define __MOTOR_H__

#include <Servo.h>

class Motor {
  public:
    Motor();

    void init(int pin, float angle);

    float calculMoteur(float cmdPHI, float cmdAlpha, double phiWire);

    void goAngle(float angle);

  private:
    Servo servo_;  
    float sectionLength_;
    float sectionRadius_;
    float wheelRadius_;
    float delta_;
    float angle_;
};

#endif

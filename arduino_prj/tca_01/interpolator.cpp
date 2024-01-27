#include "interpolator.h"

#define sq(x) ( (x)*(x) )
//#define pow(x,y) (x) // TODO
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


MotorInterpolator( int nSpeedPin, int nReversePin )
{
    nSpeedPin_ = nSpeedPin;
    nReversePin_ = nReversePin;
    rLastPwm_ = 0;
}

bool MotorInterpolator::stop()
{
    rGoal_ = 0;
    rGoalTimeMs_ = millis();
    rLastPos_ = rGoal_;
    _sendPwm(0);
}

void MotorInterpolator::_sendPwm(nVal)
{
    analogWrite(nSpeedPin_, nVal);
}

void MotorInterpolator::_sendReverse( bool bReverse )
{
    analogWrite(nReversePin_, bReverse?1:0);
}

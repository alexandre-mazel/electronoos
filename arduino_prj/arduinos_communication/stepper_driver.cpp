#include "stepper_driver.hpp"

StepperMotorInfo::StepperMotorInfo( int nNumPinEnable, int nNumPinDir, int nNumPinTrig, int nNbrStepPerTurn )
    : nNbrStepPerTurn_   ( nNbrStepPerTurn )
    , nNumPinEnable_     ( nNumPinEnable )
    , nNumPinDir_           ( nNumPinDir )
    , nNumPinTrig_          ( nNumPinTrig )
{
    dir_ = 0;
    speed_ = 0;
    timeNextTrig_ = 0;
    bNextIsHigh_ = 1;
}



SteppersDriver::SteppersDriver( int nNbrMotors )
    : nNbrMotors_       ( nNbrMotors )
{
    assert(nNbrMotors_<=STEPPER_DRIVER_NBR_MOTOR_MAX);
    initPins();
    stopAll();
}

void SteppersDriver::_initPins( void )
{
    for( int i = 0; i < nNbrMotors_; ++i )
    {
        pinMode( motors_[i].nNumPinEnable_, OUTPUT );
        pinMode( motors_[i].nNumPinDir_,      OUTPUT );
        pinMode( motors_[i].nNumPinTrig_,     OUTPUT );
    }
}
    
void SteppersDriver::order( int nNumMotor, int nDirection, int nSpeedRPM )
{
    const int i = nNumMotor;
    if( nDirection != motors_[i].dir_ )
    {
        if( motors_[i].dir_ == 0 )
        {
            digitalWrite( motors_[i].nNumPinEna_ , LOW ); // enable
        }
        else if( nDirection == 0 )
        {
            digitalWrite( motors_[i].nNumPinEna_ , HIGH ); // disable
        }
        else
        {
            digitalWrite( motors_[i].nNumPinDir_ , nDirection==1?LOW:HIGH );
        }
        
        motors_[i].dir_ = nDirection;
    }
    
    motors_[i].speed_ = nSpeedRPM;
    motors_[i].timeHalfPeriod_ = 1000000L /(motors_[i].speed_ * motors_[i].nNbrStepPerTurn_ * 2);
}

void SteppersDriver::update( void )
{
    for( int i = 0; i < nNbrMotors_; ++i )
    {
        unsigned long t = micros();
        if( motors_[i].timeNextTrig_ > t )
        {
            
            digitalWrite( motors_[i].nNumPinTrig_ , bNextIsHigh_?HIGH:LOW );
            bNextIsHigh_ = ! bNextIsHigh_;
            motors_[i].timeNextTrig_ += motors_[i].timeHalfPeriod_;
        }
    }
}

void SteppersDriver::stopAll( void )
{
    for( int i = 0; i < nNbrMotors_; ++i )
    {
        digitalWrite( motors_[i].nNumPinEna_ , HIGH ); // disable
    }
}
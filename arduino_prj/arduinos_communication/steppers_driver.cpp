#include "steppers_driver.hpp"

#include <arduino.h>

#define DEBUG 1

#define ASSERT(b) __assert((b),"__FUNC__",__FILE__,__LINE__,"");
// handle diagnostic informations given by assertion and abort program execution:
void __assert(int bTest, const char *__func, const char *__file, int __lineno, const char *__sexp) 
{
  if(bTest)
  {
    return;
  }
  Serial.println(__func);
  Serial.println(__file);
  Serial.println(__lineno, DEC);
  Serial.println(__sexp);
  Serial.flush();
  abort();
}

StepperMotorInfo::StepperMotorInfo( int nNumPinEna, int nNumPinDir, int nNumPinTrig, int nNbrStepPerTurn )
    : nNbrStepPerTurn_    ( nNbrStepPerTurn )
    , nNumPinEna_         ( nNumPinEna )
    , nNumPinDir_           ( nNumPinDir )
    , nNumPinTrig_          ( nNumPinTrig )
{
    dir_                      = 0;
    speed_                 = 0;
    timeHalfPeriod_     = 0;
    timeNextTrig_        = 0;
    bNextIsHigh_        = 1;
}

SteppersDriver::SteppersDriver( int nNbrMotors )
    : nNbrMotors_       ( nNbrMotors )
{
    ASSERT(nNbrMotors_<=STEPPERS_DRIVER_NBR_MOTOR_MAX);
    _initPins();
    stopAll();
}

void SteppersDriver::setup( int nNumMotor, int nNumPinEna, int nNumPinDir, int nNumPinTrig, int nNbrStepPerTurn )
{
    const int i = nNumMotor;
    motors_[i].nNumPinEna_ = nNumPinEna;
    motors_[i].nNumPinDir_ = nNumPinDir;
    motors_[i].nNumPinTrig_ = nNumPinTrig;
    motors_[i].nNbrStepPerTurn_ = nNbrStepPerTurn;
}

void SteppersDriver::_initPins( void )
{
    for( int i = 0; i < nNbrMotors_; ++i )
    {
        pinMode( motors_[i].nNumPinEna_, OUTPUT );
        pinMode( motors_[i].nNumPinDir_,      OUTPUT );
        pinMode( motors_[i].nNumPinTrig_,     OUTPUT );
    }
}
    
void SteppersDriver::order( int nNumMotor, int nDirection, int nSpeedRPM )
{
    const int i = nNumMotor;
    if( nDirection != motors_[i].dir_ )
    {
        
#ifdef DEBUG
        Serial.print( "INF: SteppersDriver::order: motor: ");
        Serial.print( nNumMotor );
        Serial.print( ", newdir: " );
        Serial.println( nDirection );
#endif
        
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

    } // new dir
    
    motors_[i].speed_ = nSpeedRPM;
    motors_[i].timeHalfPeriod_ = 1000000L /(motors_[i].speed_ * motors_[i].nNbrStepPerTurn_ * 2);
    motors_[i].timeNextTrig_ = micros() + motors_[i].timeHalfPeriod_;

#ifdef DEBUG
      Serial.print( "INF: SteppersDriver::order: motor: ");
      Serial.print( nNumMotor );
      Serial.print( ", speed_: " );
      Serial.print( motors_[i].speed_ );
      Serial.print( ", timeHalfPeriod_: " );
      Serial.print( motors_[i].timeHalfPeriod_ );
      Serial.print( ", timeNextTrig_: " );
      Serial.println( motors_[i].timeNextTrig_ );
#endif
}

void SteppersDriver::update( void )
{
    for( int i = 0; i < nNbrMotors_; ++i )
    {
        if(motors_[i].dir_ == 0)
        {
          continue;
        }

        unsigned long t = micros();

#ifdef DEBUG
        if(1)
        {
          Serial.print( "INF: SteppersDriver::update: t: ");
          Serial.println( t );
        }
#endif


        if( t > motors_[i].timeNextTrig_ )
        {
            
            digitalWrite( motors_[i].nNumPinTrig_ , motors_[i].bNextIsHigh_?HIGH:LOW );
            
#ifdef DEBUG
            Serial.print( "INF: SteppersDriver::update: motor: ");
            Serial.print( i );
            Serial.print( ", trigger: " );
            Serial.println( motors_[i].bNextIsHigh_?HIGH:LOW );
#endif
            motors_[i].bNextIsHigh_ = ! motors_[i].bNextIsHigh_;
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
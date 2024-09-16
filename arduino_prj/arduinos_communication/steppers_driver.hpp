// StepperDriver
// manage many stepper pwm in a single loop, pure soft (so not completely precise)
// (c) A.Mazel 2023

#ifndef _STEPPERS_DRIVER_H_
#define _STEPPERS_DRIVER_H_

#include <stdint.h>

#define STEPPERS_DRIVER_NBR_MOTOR_MAX   3

#define DIR_REVERSE         -1
#define DIR_STOP               0
#define DIR_STRAIGHT        1

class StepperMotorInfo {
    
    // A simple structure to handle information for each motor
    
    public:
        StepperMotorInfo( int nNumPinEna = -1, int nNumPinDir = -1, int nNumPinTrig = -1, int nNbrStepPerTurn = -1 );
    
        // motor config
        int                     nNbrStepPerTurn_;
        int                     nNumPinEna_;
        int                     nNumPinDir_;
        int                     nNumPinTrig_;

    
        // orders
        int                     dir_; // -1: reverse, 0: stopped, 1: running // DIR_REVERSE, DIR_STOP, DIR_STRAIGHT
        int                     speed_; // in rpm
        
        // internal
        unsigned long   timeNextTrig_; // time next trig
        int             bNextIsHigh_; // 1 if next trig is high, 0 if low
        unsigned long   timeHalfPeriod_; // time between two trig command
};

class SteppersDriver {
    
    // the motor manager.
    // Current performance on a 2560:
    // - 3 motors  stopped: seems to take 5microsec, complete loop: 17microsec (time for the fps counter)
    // - 3 motors at 1000rpm slowdown the loop of 18microsec (complete loop: at 35microsec)
    
    public:
        SteppersDriver( int nNbrMotors );
    
        void setup( int nNumMotor, int nNumPinEnable, int nNumPinDir, int nNumPinTrig, int nNbrStepPerTurn ); // setup for each motor
    
        void order( int nNumMotor, int nDirection, int nSpeedRPM ); // change speed or direction for this motor, dir = 0 => stop
    
        void update( void ); // to be called at the highest rate possible
    
        void stopAll( void ); // emergency stop

    private:
        void _initPins( void );
    
    private:
        
        StepperMotorInfo    motors_[STEPPERS_DRIVER_NBR_MOTOR_MAX];
        int                         nNbrMotors_; // how much motor to handle at this moment
};



#endif // _STEPPERS_DRIVER_H_
// StepperDriver
// manage many stepper pwm in a single loop, pure soft (so not completely precise)
// (c) A.Mazel 2023

#ifndef _STEPPER_DRIVER_H_
#define _STEPPER_DRIVER_H_

#define STEPPER_DRIVER_NBR_MOTOR_MAX   3

#define DIR_REVERSE         -1
#define DIR_STOP               0
#define DIR_STRAIGHT        1

class StepperMotorInfo {
    
    // a simple structure to handle information for each motor
    
    public:
        StepperDriverInfo( int nNumPinEnable, int nNumPinDir, int nNumPinTrig int nNbrStepPerTurn );
    
        // motor config
        int                     nNbrStepPerTurn_;
        int                     nNumPinEnable_;
        int                     nNumPinDir_;
        int                     nNumPinTrig_;

    
        // orders
        int                     dir_; // -1: reverse, 0: stopped, 1: running // DIR_REVERSE, DIR_STOP, DIR_STRAIGHT
        int                     speed_; // in rpm
        
        // internal
        unsigned long   timeNextTrig_; // time next trig
        int                     bNextIsHigh_; // 1 if next trig is high, 0 if low
        unsigned long   timeHalfPeriod_; // time between two trig command
};

class SteppersDriver {
    
    // the motor manager
    
    public:
        SteppersDriver( int nNbrMotors );
    
        void order( int nNumMotor, int nDirection, int nSpeedRPM ); // change speed or direction for this motor, dir = 0 => stop
    
        void update( void ); // to be called at the highest rate possible
    
        void stopAll( void ); // emergency stop

    private:
        void _initPins( void );
    
    private:
        
        StepperMotorInfo    motors_[STEPPER_DRIVER_NBR_MOTOR_MAX];
        int                         nNbrMotors_; // how much motor to handle at this moment
};



#endif // _STEPPER_DRIVER_H_
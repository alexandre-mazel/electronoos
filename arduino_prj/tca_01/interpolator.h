#ifndef INTERPOLATOR_H
#define INTERPOLATOR_H

#include "Arduino.h"

//#define uint8 unsigned char
typedef unsigned char uint8;
//typedef int bool;


// returns values along a bell curve from 0 - 1 - 0 with an x of 0 - 1.
float gaussian( float x );


class MotorInterpolator
{
//    public:
        
        MotorInterpolator( int nSpeedPin, int nReversePin );
        int setNewGoal( float rNewGoal, float rTime = 0.0f );  // rTime: time to reach the goal, 0. => best effort
        
        // gentle stop
        // return true if was and moving
        bool brake();
        
        
        // emergency stop
        // return true if was moving
        bool stop();
        
        // return 1 when goal reached
        bool update( float rCurPos );
    
    private:
        void _sendPwm( uint8 nVal );
        void _sendReverse( bool bReverse );
        
    int     nSpeedPin_;
    int     nReversePin_;
    float   rGoal_;
    float   rGoalTimeMs_; // ideal time in ms to reach the goal
    float   rLastPos_;
    float   rLastPwm_;
}; // class MotorInterpolator

    


#endif // INTERPOLATOR_H

    
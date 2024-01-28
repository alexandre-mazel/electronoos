#ifndef INTERPOLATOR_H
#define INTERPOLATOR_H

// de temps en temps, erase C:\Users\alexa\AppData\Local\Temp\arduino-language-server*
// et aussi C:\Users\alexa\AppData\Local\Temp\arduino\sketches\


//#define uint8 unsigned char
typedef unsigned char uint8;
//typedef int bool;


// returns values along a bell curve from 0 - 1 - 0 with an x of 0 - 1.
float gaussian( float x );


class MotorInterpolator
{
    public:
        
        MotorInterpolator( int nSpeedPin, int nReversePin );
        int setNewGoal( float rNewGoal, float rTimeSec = 0.0f );  // rTime: time to reach the goal, 0. => best effort
        
        
        // give position in revolution
        // return true when goal reached
        bool update( float rCurrentRev );
    
    
        // gentle stop
        // return true if was and moving
        bool brake();
        
        
        // emergency stop
        // return true if was moving
        bool stop();


        bool isMoving(void) {return nLastPwm_ > 0;}
        bool isArrived(void);
        bool getPos(void) {return rLastPos_;}

    private:
        void _sendPwm( uint8 nVal );
        void _sendReverse( bool bReverse );
        
    int       nSpeedPin_;
    int       nReversePin_;
    float     rGoal_;
    long int  nTimeStartMove_; // time receive current goal
    float     rGoalTimeMs_; // ideal time in ms to reach the goal
    float     rLastPos_;
    uint8     nLastPwm_;

}; // class MotorInterpolator

    


#endif // INTERPOLATOR_H

    
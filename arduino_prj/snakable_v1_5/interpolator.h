#ifndef __INTERPOLATOR_H__
#define __INTERPOLATOR_H__

// all times are in ms
typedef signed long timeunit; // ms stored to signed long => (overflow after 25 days)

class Interpolator
{
    public:
        
        Interpolator();
        
        float   update( timeunit time_ms ); // update values and return the value
        int      isFinished( void ) const {return bIsFinished_;};
        float   getPos( void ) const {return rPos_;};
        void    setRelGoal( float rGoalPos, timeunit tGoalRel );  // set absolute goal position
        void    setAbsGoal( float rGoalPos, timeunit tGoalRel ); // set goal relative to current one position
    
        void    print(void);
        
        static void autoTest(void); // not really a complete autotest, but permits to check it's quite working
    
    private:
        int    bIsFinished_;
        float rPos_; // current pos
        float rStartPos_;
        float rGoalPos_;
    
        timeunit  rStartTime_;
        timeunit  rGoalTime_;
};



#endif // __INTERPOLATOR_H__
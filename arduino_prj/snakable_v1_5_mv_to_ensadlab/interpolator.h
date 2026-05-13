#ifndef __INTERPOLATOR_H__
#define __INTERPOLATOR_H__

// all times are in ms
typedef signed long timetype; // ms stored to signed long => (overflow after 25 days)

class Interpolator
{
    public:
        
        Interpolator();
        
        float   update( timetype current_time_ms ); // update values and return if it's finished
        int      isFinished( void ) const {return bIsFinished_;};
        void   forcePos( float pos ) {rPos_ = pos;};
        float   getPos( void ) const {return rPos_;};
        float   getVal( void ) const {return rPos_;};
        void    setRelGoal( float rGoalPos, timetype tGoalRel );  // set absolute goal position
        void    setAbsGoal( float rGoalPos, timetype tGoalRel ); // set goal relative to current one position
        
        void    setPingpong( bool bEnable ) { bPingPong_= bEnable; };
        void    setSpline( bool bEnable ) { bSpline_= bEnable; };
    
        void    print(void);
        
        static void autoTest(void); // not really a complete autotest, but permits to check it's quite working
    
    private:
        int    bIsFinished_;
        float rPos_; // current pos
        float rStartPos_;
        float rGoalPos_;
    
        timetype  rStartTime_;
        timetype  rGoalTime_;
    
        int         bPingPong_;
        int         bSpline_;
};


class InterpolatorManager
{
  public:
    InterpolatorManager();
    ~InterpolatorManager();

    void init( int nNbrInterpolator );

    update( timetype current_time_ms );

  private:
    Interpolator *  pInterpolators_;
    int             nNbrInterpolator_;
};

extern InterpolatorManager interpolatorManager; // a singleton to manage all interpolators of our programs



#endif // __INTERPOLATOR_H__
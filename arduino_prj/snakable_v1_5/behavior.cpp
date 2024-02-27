#include "behavior.h"

#include "interpolator.h"

Behavior::Behavior()
  : bRunning_      ( false )
  , bPaused_        ( false )
  , rArousal_        ( 0.f )
  , rValence_        ( 0.f )
  , rSpeed_          ( 0.f )
  , rAmp_            ( 0.f )
  , rCongruence_  ( 0.f )
  , rRest_            ( 0.f )
  , rRepeat_         ( 0.f )
{

}
void Behavior::init()
{

}

void Behavior::start()
{
  
}


void Behavior::stop()
{

}

void Behavior::pause()
{
  
}

void Behavior::resume()
{

}

void Behavior::update( unsigned long t_ms, const ColorSensor & colorSensor )
{

    _udpateExternalVar();
    
}

void Behavior::_udpateExternalVar()
{
    rSpeed_ = (rArousal_+1 ) / 2.f;
    rAmp_ = (rArousal_+1 ) / 2.f;
    rRest_ = 1 - ( (rArousal_+1 ) / 2.f );
    
    rCongruence_ = (rValence_+1 ) / 2.f;
    rRepeat_ = (rValence_+1 ) / 2.f;
}

void Behavior::_sendMoves()
{
    
}
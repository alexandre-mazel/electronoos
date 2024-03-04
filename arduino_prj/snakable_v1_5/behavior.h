#ifndef __BEHAVIOR_H__
#define __BEHAVIOR_H__

#include "color_sensor.h"

class Behavior 
{
	public:
		Behavior();
		void init();

		void start();

		void stop();

    void pause();
    void resume();

    void update( unsigned long t_ms, const ColorSensor & colorSensor );
  
  private:
      void _udpateInternalVar(const ColorSensor & colorSensor); // TODO update rArousal_ & rValence_ relatively to external stimuli
      void _udpateExternalVar();
      void _sendMoves();
    
  private:
    bool bRunning_;
    bool bPaused_;
  
    //signed long timeLastOrder_; // todo
  
    // Inner variables [-1..1]
    float rArousal_;            // sleepy <--> excited => speed ++, amp ++, rest--
    float rValence_;            // angry <--> happy => congruence ++, repeat ++
  
    // External variables [0..1]
    float rSpeed_;              // speed
    float rAmp_;                // amplitude
    float rCongruence_;     // similarity of behavior between the two moving sections
    float rRest_;               // wait between each moves
    float rRepeat_;           // repetition of same movement
};

#endif __BEHAVIOR_H__

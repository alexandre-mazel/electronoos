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
    bool bRunning_;
    bool bPaused_;

};

#endif __BEHAVIOR_H__

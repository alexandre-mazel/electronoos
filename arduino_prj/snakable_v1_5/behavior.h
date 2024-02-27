#ifndef __BEHAVIOR_H__
#define __BEHAVIOR_H__

class Behavior 
{
	public:
		Behavior();
		void init();

		void start();

		void stop();

    void pause();
    void resume();

    void update( unsigned long t );

  private:
    bool bRunning_;
    bool bPaused_;

};

#endif __BEHAVIOR_H__

#ifndef _MOTION_DETECTION_H_
#define _MOTION_DETECTION_H_

#include <Arduino.h>

//////
//  o GND
//  o Sensor Pin 12 (5V)
//  o VCC (5V)
//////

class MotionDetection 
{
  public:
    MotionDetection(unsigned int pin, byte counter_max);
    void update();

    void print();

  private:
    boolean sleep_mode_;
    boolean last_state_;
    boolean motion_;

    unsigned long counter_;
    unsigned int  sensor_pin_;
    uint8_t       count_;
    uint16_t      max_count_;
    boolean       pir_;
};

#endif

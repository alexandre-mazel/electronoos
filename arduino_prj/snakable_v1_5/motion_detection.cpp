#include "motion_detection.h"
#include "definitions.h"

MotionDetection::MotionDetection(unsigned int pin, byte counter_max) 
  :sleep_mode_ ( true )
  ,last_state_ ( false )
  ,motion_ (false )
  ,counter_ ( 0 )
  ,sensor_pin_( pin )
  ,count_ ( 0 )
  ,max_count_ ( 0 )
  ,pir_ ( false )
  {

#ifdef _DEBUG
    counter_max = 2;
    pinMode(sensor_pin_, INPUT_PULLUP);
#else
    pinMode(sensor_pin_, INPUT);
#endif
    max_count_ = counter_max * 10;
  }

void MotionDetection::update() 
{
  pir_ = digitalRead(sensor_pin_);
  //motion_ = (frc.f_mPir) ? frc.f_vPir : pir_; // TODO Alma: c'est quoi ?

  // If motion and in sleep mode, wake up
  if (motion_) {
    if (motion_ != last_state_) {
      count_ = counter_ = 0;
      Serial.println("Motion detected");
    }
    if (sleep_mode_) {
      sleep_mode_ = false;
      Serial.println("Wake up");
    }
  }
  else {
    if (motion_ != last_state_) {
      count_ = counter_ = 0;
      Serial.println("PIR counter reset");
    }
    else {
      if (!sleep_mode_) {
        counter_++;
        if (counter_ % TIME_MOTION_INC == 0) {
          count_++;
          if (count_ % 10 == 0) {
            Serial.print("PIR counter (s) : ");
            Serial.println(count_);
          }
          if (count_ == max_count_) {
            sleep_mode_ = true;
            Serial.println("Sleep");
            count_ = 0;
          }
        }
      }
    }
  }
  last_state_ = motion_;
}

void MotionDetection::print() 
{
  Serial.print("Sleep mode : ");
  Serial.println(sleep_mode_ ? "ON" : "OFF");
}
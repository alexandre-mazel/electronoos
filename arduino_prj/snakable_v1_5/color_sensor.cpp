#ifndef __COLORSENSOR_H__
#define __COLORSENSOR_H__

#include <Wire.h>
#include <math.h>
#include "SparkFun_APDS9960.h"

//////
//  o GND
//  o VCC (3.3V)
//  o SDA (3.3V)
//  o SCL (3.3V)
//////

float rgb2hue(int r, int g, int b) 
{
  float h = 0.0f;
  int cmax = r;
  if (g > cmax) cmax = g;
  if (b > cmax) cmax = b;
  int cmin = r;
  if (g < cmin) cmin = g;
  if (b < cmin) cmin = b;

  if (cmin == cmax) {
    return h;
  }

  if (r >= cmax) {
    h = (float)(g - b) / (cmax - cmin); //%6 inutile !?
  }
  else if (g >= cmax) {
    h = 2.0 + (float)(b - r) / (cmax - cmin);
  }
  else if (b >= cmax) {
    h = 4.0 + (float)(r - g) / (cmax - cmin);
  }
  return h * 60.0f;
}


ColorSensor::ColorSensor() 
  :apds_ ( SparkFun_APDS9960() )
  ,enabled_(false)
  ,ambient_(0)
  ,red_(0)
  ,green_(0)
  ,blue_(0)
  ,hue_(0.0f)
  ,light_(0.0f)
  ,lightCoef_(0.92f)
  ,deltaLight_(0.0f)
{

}

boolean ColorSensor::init() 
{
  enabled_ = apds.init();
  if (enabled_) {
    enabled_ = apds.enableLightSensor(false);
  }
  // Wait for initialization and calibration to finish
  delay(500);
  return enabled_;
}

void ColorSensor::update() 
{
  //int prevA = (int)ambient_;
  //float prevL = light_;

  if (enabled_) 
  {

    if (!apds.readAmbientLight(ambient_) ||
      !apds.readRedLight(red_) ||
      !apds.readGreenLight(green_) ||
      !apds.readBlueLight(blue_)
    )
    {
      Serial.println("Error reading light values");
      return;
    }
  }
  else 
  {
    //Serial.println("Mode simulation");
    red_ = random(1024); green_ = random(1024); blue_ = random(1024); ambient_ = random(1024);
  }

  hue_ = rgb2hue(red_, green_, blue_);
  deltaLight_ = abs((float)ambient-light); 
  light_ = light_ * lightCoef_ + (1.0f - lightCoef_)*(float)ambient_;        
}
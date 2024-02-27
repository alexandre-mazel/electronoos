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
  enabled = apds.init();
  if (enabled) {
    enabled = apds.enableLightSensor(false);
  }
  // Wait for initialization and calibration to finish
  delay(500);
  return enabled;
}

void ColorSensor::update() 
{
  if (enabled) {
    int prevA = (int)ambient;
    float prevL = light;
    if (!apds.readAmbientLight(ambient) ||
      !apds.readRedLight(red) ||
      !apds.readGreenLight(green) ||
      !apds.readBlueLight(blue) ) {
      //Serial.println("Error reading light values");
    } else {
      hue = rgb2hue(red, green, blue);
      deltaLight = abs((float)ambient-light); 
      light = light * lightCoef + (1.0f - lightCoef)*(float)ambient;
      //deltaLight = abs( (int)ambient-prevL );
    }
  }
  else {
    //Serial.println("Mode simulation");
    int prevA = (int)ambient;
    float prevL = light;
    red = random(1024); green = random(1024); blue = random(1024); ambient = random(1024);
    hue = rgb2hue(red, green, blue);
    deltaLight = abs((float)ambient-light); 
    light = light * lightCoef + (1.0f - lightCoef)*(float)ambient;        
  }
}
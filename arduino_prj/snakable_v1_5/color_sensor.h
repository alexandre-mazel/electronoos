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

class ColorSensor 
{
	public:
		ColorSensor();

		boolean init()
		void update();

  private:
  	SparkFun_APDS9960   apds_;
		boolean             enabled_;
		uint16_t            ambient_;
		uint16_t            red_;
		uint16_t            green_;
		uint16_t            blue_;
		float	              hue_;
		float	              light_;
		float	              lightCoef_;
		float	              deltaLight_;
};

#endif // __COLORSENSOR_H__

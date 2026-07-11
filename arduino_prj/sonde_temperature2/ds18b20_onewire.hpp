#ifndef __DS18B20_ONEWIRE_H__
#define __DS18B20_ONEWIRE_H__

int OneWire_setup( void );
int OneWire_getAllTemperature( float * pTemp1, float * pTemp2 = NULL, float * pTemp3 = NULL, float * pTemp4 = NULL, float * pTemp5 = NULL);

#endif
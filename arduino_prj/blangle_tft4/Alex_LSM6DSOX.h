#ifndef _ALEX_LSM6DSOX_H
#define _ALEX_LSM6DSOX_H
 
#include "Adafruit_LSM6DSOX.h" // seen in C:\Users\alexa\Documents\Arduino\libraries\Adafruit_LSM6DS
 
 
typedef struct Sensors
{
    sensors_event_t accel_;
    sensors_event_t gyro_;
    sensors_event_t temp_;
} t_sensors;

 class Alex_LSM6DSOX : public Adafruit_LSM6DSOX {
  public:
    Alex_LSM6DSOX( const char* pNickName = NULL ); // you can specify a nick name to this sensor

    bool begin_I2C(uint8_t i2c_addr = LSM6DS_I2CADDR_DEFAULT);

    void printConfig( void );
    
    void update( void );      // call to read values (immediate)

    float getDegY( void ) const;    // get Last measured Y in degrees

    void printValues( void ) const; // print last updated values

  private:

    const char* pNickName_; // personal name of this sensor (for debug)
    
    uint8_t     i2c_addr_;
    bool bFound_;                   // set to false while not correctly inited (by begin_I2C)
    char nNbrMissedUpdate_;     // inc on read error
    char filler[1];                     // padding a la mano
  


    sensors_event_t accel_;
    sensors_event_t gyro_;
    sensors_event_t temp_;
  
    float rPrevDegY_;

 };
 
 #endif
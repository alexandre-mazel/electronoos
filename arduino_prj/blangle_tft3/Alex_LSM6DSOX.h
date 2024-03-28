#ifndef _ALEX_LSM6DSOX_H
 #define _ALEX_LSM6DSOX_H
 
 #include "Adafruit_LSM6DSOX.h" // seen in C:\Users\alexa\Documents\Arduino\libraries\Adafruit_LSM6DS
 
 
 class Alex_LSM6DSOX : public Adafruit_LSM6DSOX {
  public:
    Alex_LSM6DSOX( const char* pNickName = NULL ); // you can specify a nick name to this sensor

    bool begin_I2C(uint8_t i2c_addr = LSM6DS_I2CADDR_DEFAULT);

    void printConfig( void );
    void printValues( void );

    void update( void );

  private:

  const char* pNickName_; // personal name of this sensor (for debug)
 };
 
 #endif
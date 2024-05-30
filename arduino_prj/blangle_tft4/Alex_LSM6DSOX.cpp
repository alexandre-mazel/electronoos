#include "Arduino.h"
#include <Wire.h>
#include "Alex_LSM6DSOX.h"

// #define ALEX_MSM6DSOX_ALL_DEBUG_CODE // define me to include all debug code (increase static code size)

Alex_LSM6DSOX::Alex_LSM6DSOX(const char* pNickName)
  : Adafruit_LSM6DSOX ()
  , pNickName_            ( pNickName )
  , bFound_               ( false )
  , nNbrMissedUpdate_     ( 0 )
{


}

bool Alex_LSM6DSOX::begin_I2C(uint8_t i2c_addr)
{
    Serial.print("Alex_LSM6DSOX::begin_I2C '");
    i2c_addr_ = i2c_addr;
    if(pNickName_!=NULL) Serial.print(this->pNickName_);

    Serial.print( ", this: "); Serial.print((int)this);
    Serial.print( ", i2c_addr: "); Serial.print((int)i2c_addr,HEX);

    if( Adafruit_LSM6DSOX::begin_I2C(i2c_addr) )
    {
        Serial.println("': Success !");
        bFound_ = true;
        return true;
    }
    Serial.println("': Failure!");
    return false;
}


void Alex_LSM6DSOX::printConfig( void )
{
  Serial.print("Alex_LSM6DSOX.printConfig '");
  if(pNickName_!=NULL) Serial.print(this->pNickName_);
  Serial.println("': ");
  if( ! bFound_ )
  {
    Serial.println("Not initialised");
    return;
  }

  #ifdef ALEX_MSM6DSOX_ALL_DEBUG_CODE

  // this->setAccelRange(LSM6DS_ACCEL_RANGE_2_G);
  Serial.print("Accelerometer range set to: ");
  switch (this->getAccelRange()) {
  case LSM6DS_ACCEL_RANGE_2_G:
    Serial.println("+-2G");
    break;
  case LSM6DS_ACCEL_RANGE_4_G:
    Serial.println("+-4G");
    break;
  case LSM6DS_ACCEL_RANGE_8_G:
    Serial.println("+-8G");
    break;
  case LSM6DS_ACCEL_RANGE_16_G:
    Serial.println("+-16G");
    break;
  }

  // this->setGyroRange(LSM6DS_GYRO_RANGE_250_DPS );
  Serial.print("Gyro range set to: ");
  switch (this->getGyroRange()) {
  case LSM6DS_GYRO_RANGE_125_DPS:
    Serial.println("125 degrees/s");
    break;
  case LSM6DS_GYRO_RANGE_250_DPS:
    Serial.println("250 degrees/s");
    break;
  case LSM6DS_GYRO_RANGE_500_DPS:
    Serial.println("500 degrees/s");
    break;
  case LSM6DS_GYRO_RANGE_1000_DPS:
    Serial.println("1000 degrees/s");
    break;
  case LSM6DS_GYRO_RANGE_2000_DPS:
    Serial.println("2000 degrees/s");
    break;
  case ISM330DHCX_GYRO_RANGE_4000_DPS:
    break; // unsupported range for the DSOX
  }

  // this->setAccelDataRate(LSM6DS_RATE_12_5_HZ);
  Serial.print("Accelerometer data rate set to: ");
  switch (this->getAccelDataRate()) {
  case LSM6DS_RATE_SHUTDOWN:
    Serial.println("0 Hz");
    break;
  case LSM6DS_RATE_12_5_HZ:
    Serial.println("12.5 Hz");
    break;
  case LSM6DS_RATE_26_HZ:
    Serial.println("26 Hz");
    break;
  case LSM6DS_RATE_52_HZ:
    Serial.println("52 Hz");
    break;
  case LSM6DS_RATE_104_HZ:
    Serial.println("104 Hz");
    break;
  case LSM6DS_RATE_208_HZ:
    Serial.println("208 Hz");
    break;
  case LSM6DS_RATE_416_HZ:
    Serial.println("416 Hz");
    break;
  case LSM6DS_RATE_833_HZ:
    Serial.println("833 Hz");
    break;
  case LSM6DS_RATE_1_66K_HZ:
    Serial.println("1.66 KHz");
    break;
  case LSM6DS_RATE_3_33K_HZ:
    Serial.println("3.33 KHz");
    break;
  case LSM6DS_RATE_6_66K_HZ:
    Serial.println("6.66 KHz");
    break;
  }

  // this->setGyroDataRate(LSM6DS_RATE_12_5_HZ);
  Serial.print("Gyro data rate set to: ");
  switch (this->getGyroDataRate()) {
  case LSM6DS_RATE_SHUTDOWN:
    Serial.println("0 Hz");
    break;
  case LSM6DS_RATE_12_5_HZ:
    Serial.println("12.5 Hz");
    break;
  case LSM6DS_RATE_26_HZ:
    Serial.println("26 Hz");
    break;
  case LSM6DS_RATE_52_HZ:
    Serial.println("52 Hz");
    break;
  case LSM6DS_RATE_104_HZ:
    Serial.println("104 Hz");
    break;
  case LSM6DS_RATE_208_HZ:
    Serial.println("208 Hz");
    break;
  case LSM6DS_RATE_416_HZ:
    Serial.println("416 Hz");
    break;
  case LSM6DS_RATE_833_HZ:
    Serial.println("833 Hz");
    break;
  case LSM6DS_RATE_1_66K_HZ:
    Serial.println("1.66 KHz");
    break;
  case LSM6DS_RATE_3_33K_HZ:
    Serial.println("3.33 KHz");
    break;
  case LSM6DS_RATE_6_66K_HZ:
    Serial.println("6.66 KHz");
    break;
  }
  
#endif
}


void Alex_LSM6DSOX::update( void )
{
    //  Get a new normalized sensor event

    //int32_t timestamp_prev = accel_.timestamp;
    float prev_temp = temp_.temperature;

    this->getEvent(&accel_, &gyro_, &temp_);

    //Serial.print("temp_.timestamp: "); Serial.println(temp_.timestamp);
    //Serial.print("temp_.temperature: "); Serial.println(temp_.temperature);
    
    //if( accel_.timestamp == timestamp_prev ) // so sad: timestamp is updated even when no read!

    if( prev_temp == temp_.temperature || temp_.sensor_id <= 0 || temp_.sensor_id > 3 )
    {
        Serial.print("nNbrMissedUpdate_: "); Serial.println( (int)nNbrMissedUpdate_ ); 
        ++nNbrMissedUpdate_;
        if( nNbrMissedUpdate_ > 20 )
        {
            nNbrMissedUpdate_ = 0;
            begin_I2C(i2c_addr_);
        }
        else if( nNbrMissedUpdate_ > 3 )
        {
            bFound_ = false;
        }
    }
    else 
    {
        // success
        nNbrMissedUpdate_ = 0;
        if( ! bFound_ )
        {
            bFound_ = true;
        }
        
        const float g = 9.806f;
  
        //float r = accel_.acceleration.z*90/9.81f;
        float r = accel_.acceleration.y-gyro_.gyro.y;
        if(r<-g)
        {
            r = -90.f;
        }
        else if(r>g)
        {
            r = 90.f;
        }
        else
        {
            r = asin((r)/g)*180/PI;
        }
        //~ if( isnan(r) )
        //~ {
            //~ r = 90.f; // too much acceleration
        //~ }
        rPrevDegY_ = r*0.5f + rPrevDegY_ * 0.5f;  // avg roughly on 5 values
    }
}

float Alex_LSM6DSOX::getDegY( void ) const
{
  if(!bFound_)
  {
    return 6666.6f;
  }
  return rPrevDegY_;
}

void Alex_LSM6DSOX::printValues( void ) const
{

  Serial.print("Alex_LSM6DSOX.printValues '");
  if(pNickName_!=NULL) Serial.print(this->pNickName_);
  Serial.println("': ");

  if(!bFound_)
  {
    Serial.println("Not initialised");
    return;
  }
  
//#ifdef ALEX_MSM6DSOX_ALL_DEBUG_CODE
  Serial.print("\tsensor_id: ");
  Serial.println(temp_.sensor_id);
  
  Serial.print("\ttimestamp: ");
  Serial.println(temp_.timestamp);
//#endif

  

  Serial.print("\tTemperature ");
  Serial.print(temp_.temperature);
  Serial.println(" deg C");

#ifdef ALEX_MSM6DSOX_ALL_DEBUG_CODE

  // Display the results (acceleration is measured in m/s^2)
  Serial.print("\tAccel X: ");
  Serial.print(accel_.acceleration.x);
  
#endif
  
  Serial.print(" \tY: ");
  Serial.print(accel_.acceleration.y);
  
  Serial.print(" \tZ: ");
  Serial.print(accel_.acceleration.z);
  Serial.println(" m/s^2 ");
  
#ifdef ALEX_MSM6DSOX_ALL_DEBUG_CODE

  // Display the results (rotation is measured in rad/s)
  Serial.print("\tGyro X: ");
  Serial.print(gyro_.gyro.x);
  Serial.print(" \tY: ");
  Serial.print(gyro_.gyro.y);
  Serial.print(" \tZ: ");
  Serial.print(gyro_.gyro.z);
  Serial.println(" radians/s ");
  Serial.println();
#endif
  
}

#include "Arduino.h"
#include <Wire.h>
#include "Alex_LSM6DSOX.h"

Alex_LSM6DSOX::Alex_LSM6DSOX(const char* pNickName)
  : Adafruit_LSM6DSOX ()
  , pNickName_        ( pNickName )
  , bFound_           ( false )
{

}

bool Alex_LSM6DSOX::begin_I2C(uint8_t i2c_addr)
{
  Serial.print("Alex_LSM6DSOX::begin_I2C '");
  if(pNickName_!=NULL) Serial.print(this->pNickName_);

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
  if(!bFound_)
  {
    Serial.println("Not initialised");
    return;
  }

  return; // comment to gain code size

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
}


void Alex_LSM6DSOX::update( void )
{
  //  Get a new normalized sensor event
  this->getEvent(&accel_, &gyro_, &temp_);
}

float Alex_LSM6DSOX::getDegZ( void ) const
{
  if(!bFound_)
  {
    return 666.6f;
  }
  const float g = 9.806f;
  //return accel_.acceleration.z*90/9.81f;
  return asin(accel_.acceleration.z/g)*180/PI;
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

  

  Serial.print("\tTemperature ");
  Serial.print(temp_.temperature);
  Serial.println(" deg C");

  /*

  // Display the results (acceleration is measured in m/s^2)
  Serial.print("\tAccel X: ");
  Serial.print(accel_.acceleration.x);
  Serial.print(" \tY: ");
  Serial.print(accel_.acceleration.y);
  */
  Serial.print(" \tZ: ");
  Serial.print(accel_.acceleration.z);
  Serial.println(" m/s^2 ");
  /*

  // Display the results (rotation is measured in rad/s)
  Serial.print("\tGyro X: ");
  Serial.print(gyro_.gyro.x);
  Serial.print(" \tY: ");
  Serial.print(gyro_.gyro.y);
  Serial.print(" \tZ: ");
  Serial.print(gyro_.gyro.z);
  Serial.println(" radians/s ");
  Serial.println();
  */
  
}

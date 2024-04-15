/* 
  Copyright 2020, Nikolas Lamb. 

  scan_dynamixel_and_flash
    This is a great program (mostly) by ROBOTIS to help find out if your servos  
    are connected properly. Unfortunately, if you're using an UNO it doesn't 
    work because the Dynamixels disrupt serial communication. 
    
    This program circumvents this problem by flashing leds on dynamixels that
    are successfully found by the shield. Just a quick way to check if 
    everything is properly connected. 
*/
#include <DynamixelShield.h>

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)
  #include <SoftwareSerial.h>
  SoftwareSerial soft_serial(7, 8); // DYNAMIXELShield UART RX/TX
  #define DEBUG_SERIAL soft_serial
#elif defined(ARDUINO_SAM_DUE) || defined(ARDUINO_SAM_ZERO)
  #define DEBUG_SERIAL SerialUSB
#else
  #define DEBUG_SERIAL Serial
#endif

#if 0
  #define MAX_BAUD 5
  const int32_t buad[MAX_BAUD] = {57600, 115200, 1000000, 2000000, 3000000}; //  on my board it stuck at 2M id0
#else
  #define MAX_BAUD 4
  const int32_t buad[MAX_BAUD] = {9600, 57600, 115200, 1000000}; // default for 430 is 57600
#endif

#define nMotorBaudRate 1000000
#define nMotorProtocol 1

const int nMotorId = 46;

#define REG_TORQUE_ENABLE 0X18
#define REG_CW_COMPLIANCE_MARGIN 0X1A
#define REG_CCW_COMPLIANCE_MARGIN 0X1B

#define REG_MOVING_SPEED_LBITS 0X20
#define REG_MOVING_SPEED_HBITS 0X21

#define REG_MAX_TORQUE_LBITS 0X22
#define REG_MAX_TORQUE_HBITS 0X23


Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

void setup() {
  // put your setup code here, to run once:
  int8_t index = 0;
  int8_t found_dynamixel = 0;
  
  // Use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(115200);   //set debugging port baudrate to 115200bps
  //while(!DEBUG_SERIAL);         //Wait until the serial port is opened


  dxl.setPortProtocolVersion((float)nMotorProtocol);
  DEBUG_SERIAL.print("SCAN PROTOCOL ");
  DEBUG_SERIAL.println(nMotorProtocol);

  DEBUG_SERIAL.print("SCAN BAUDRATE ");
  DEBUG_SERIAL.println(nMotorBaudRate);
  dxl.begin(nMotorBaudRate);

  if(0)
  {
    dxl.torqueOff(nMotorId);
    dxl.setOperatingMode(nMotorId, OP_POSITION);
    dxl.setOperatingMode(nMotorId, OP_VELOCITY);
    dxl.torqueOn(nMotorId);
    dxl.setGoalVelocity(nMotorId, 100, UNIT_PERCENT);

    int nNbrLoop = 60; // 60 sec
    nNbrLoop = 2;
    for(int i = 0; i < nNbrLoop; ++i)
    {
      dxl.ledOn(nMotorId);
      delay(500);
      dxl.ledOff(nMotorId);
      delay(500);
    }

    dxl.setGoalVelocity(nMotorId, 0, UNIT_PERCENT);
    dxl.torqueOff(nMotorId);

    delay(2000);
  }
  if(1)
  {
    // fast ping pong
    dxl.torqueOff(nMotorId);
    dxl.setOperatingMode(nMotorId, OP_VELOCITY);
    dxl.torqueOn(nMotorId);
    dxl.setGoalVelocity(nMotorId, 100, UNIT_PERCENT);
    delay(2000);
    //dxl.setGoalVelocity(nMotorId, -10, UNIT_PERCENT); // WRN: bug in the lib for protocol 1 wirh negative values
    dxl.setGoalVelocity(nMotorId, 1023, UNIT_RAW); // 50: very slow reverse, 1023: fast reverse, 1074: slow straight, 2047: fast straight
    delay(2000);
    //dxl.setGoalVelocity(nMotorId, 0, UNIT_PERCENT);
    //delay(2000);
    dxl.torqueOff(nMotorId);
  }

  if(1)
  {
    // very slow move
    dxl.torqueOff(nMotorId);
    dxl.setOperatingMode(nMotorId, OP_VELOCITY);
    dxl.torqueOn(nMotorId);
    dxl.setGoalVelocity(nMotorId, 10, UNIT_PERCENT);
    //dxl.setGoalVelocity(nMotorId, 1126, UNIT_RAW); // this line block the upload !!! (nearly at the end timeout)
    delay(4000);
    //dxl.setGoalVelocity(nMotorId, -10, UNIT_PERCENT); // WRN: bug in the lib for protocol 1 wirh negative values
    dxl.setGoalVelocity(nMotorId, 102, UNIT_RAW); // 50: very slow reverse, 1023: fast reverse, 1074: slow straight, 2047: fast straight
    delay(4000);
    //dxl.setGoalVelocity(nMotorId, 0, UNIT_PERCENT);
    //delay(2000);
    dxl.torqueOff(nMotorId);
  }
  if(0)
  {
    dxl.torqueOff(nMotorId);
    //dxl.setOperatingMode(nMotorId, OP_POSITION); // moves
    //dxl.setOperatingMode(nMotorId, OP_EXTENDED_POSITION); // moves
    dxl.setOperatingMode(nMotorId, OP_CURRENT_BASED_POSITION); // no moves
    //dxl.setOperatingMode(nMotorId, OP_VELOCITY); // no moves (as we don't send velocity order)
    //dxl.setOperatingMode(nMotorId, OP_CURRENT); // no moves (not available in ax12a ?)
    
    dxl.torqueOn(nMotorId);


    dxl.writeControlTableItem(REG_TORQUE_ENABLE, nMotorId, 1);
    dxl.writeControlTableItem(REG_MAX_TORQUE_HBITS, nMotorId, 0);
    dxl.writeControlTableItem(REG_MAX_TORQUE_LBITS, nMotorId, 0);

    // Set Goal Current 3.0% using percentage (-100.0 [%] ~ 100.0[%])
    dxl.setGoalCurrent(nMotorId, 5.0, UNIT_PERCENT);
    dxl.setGoalPosition(nMotorId, +180.0, UNIT_DEGREE);
    dxl.writeControlTableItem(REG_TORQUE_ENABLE, nMotorId, 1);
    dxl.writeControlTableItem(REG_MAX_TORQUE_HBITS, nMotorId, 0);
    dxl.writeControlTableItem(REG_MAX_TORQUE_LBITS, nMotorId, 0x01); // moves with 1 and not with 0
    dxl.writeControlTableItem(REG_CW_COMPLIANCE_MARGIN, nMotorId, 0x7F);
    dxl.writeControlTableItem(REG_CCW_COMPLIANCE_MARGIN, nMotorId, 0x7F);

    dxl.writeControlTableItem(REG_MOVING_SPEED_HBITS, nMotorId, 0x0);
    dxl.writeControlTableItem(REG_MOVING_SPEED_LBITS, nMotorId, 0x1);

    delay(2000);

    dxl.setGoalPosition(nMotorId, +0.0, UNIT_DEGREE);
    delay(2000);

    dxl.setGoalCurrent(nMotorId, -5.0, UNIT_PERCENT);
    dxl.setGoalPosition(nMotorId, -180.0, UNIT_DEGREE);
    delay(2000);

    dxl.torqueOff(nMotorId);
  }

  if(0)
  {
    // fonctionne pas sur ax12a
    dxl.torqueOff(nMotorId);
    dxl.setOperatingMode(nMotorId, OP_CURRENT);
    dxl.torqueOn(nMotorId);

    // Set Goal Current 3.0% using percentage (-100.0 [%] ~ 100.0[%])
    dxl.setGoalCurrent(nMotorId, -50.0, UNIT_PERCENT);
    delay(2000);

    dxl.torqueOff(nMotorId);
  }

  DEBUG_SERIAL.print("ID: ");
  DEBUG_SERIAL.print(nMotorId);
  DEBUG_SERIAL.print(", Model Number: ");
  DEBUG_SERIAL.println(dxl.getModelNumber(nMotorId));
}

void loop() {
  // put your main code here, to run repeatedly:
}
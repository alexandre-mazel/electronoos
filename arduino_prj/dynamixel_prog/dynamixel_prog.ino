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

  dxl.torqueOff(nMotorId);
  dxl.setOperatingMode(nMotorId, OP_POSITION);
  dxl.setOperatingMode(nMotorId, OP_VELOCITY);
  dxl.torqueOn(nMotorId);
  dxl.setGoalVelocity(nMotorId, 100, UNIT_PERCENT);


  for(int i = 0; i < 60; ++i)
  {
    dxl.ledOn(nMotorId);
    delay(500);
    dxl.ledOff(nMotorId);
    delay(500);
  }

  dxl.setGoalVelocity(nMotorId, 0, UNIT_PERCENT);
  dxl.torqueOff(nMotorId);

  DEBUG_SERIAL.print("ID: ");
  DEBUG_SERIAL.print(nMotorId);
  DEBUG_SERIAL.print(", Model Number: ");
  DEBUG_SERIAL.println(dxl.getModelNumber(nMotorId));
}

void loop() {
  // put your main code here, to run repeatedly:
}
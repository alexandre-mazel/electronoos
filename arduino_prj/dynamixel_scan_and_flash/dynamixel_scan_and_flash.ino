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


Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

void setup() {
  // put your setup code here, to run once:
  int8_t index = 0;
  int8_t found_dynamixel = 0;
  
  // Use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(115200);   //set debugging port baudrate to 115200bps
  while(!DEBUG_SERIAL);         //Wait until the serial port is opened

  DEBUG_SERIAL.println("dynamixel_scan_and_flash.ino v0.6. Setup starting...");

  DEBUG_SERIAL.println("INF: Scanning...");

    
  for(int8_t protocol = 1; protocol < 3; protocol++) {
    // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.

    DEBUG_SERIAL.print("Serial: ");
    DEBUG_SERIAL.println(Serial);

  //  DEBUG_SERIAL.print("Serial1: ");
  //  DEBUG_SERIAL.println(Serial1);

    DEBUG_SERIAL.print("DXL_SERIAL: ");
    DEBUG_SERIAL.println(DXL_SERIAL);


    DEBUG_SERIAL.print("DXL_DIR_PIN: ");
    DEBUG_SERIAL.println(DXL_DIR_PIN);

    dxl.setPortProtocolVersion((float)protocol);
    DEBUG_SERIAL.print("SCAN PROTOCOL ");
    DEBUG_SERIAL.println(protocol);
    
    for(index = 0; index < MAX_BAUD; index++) {
      // Set Port baudrate.
      DEBUG_SERIAL.print("SCAN BAUDRATE ");
      DEBUG_SERIAL.println(buad[index]);
      dxl.begin(buad[index]);
      for(int id = 0; id < DXL_BROADCAST_ID; id++) {
        //iterate until all ID in each buadrate is scanned.
        //DEBUG_SERIAL.println(id);
        if(dxl.ping(id)) {

          dxl.torqueOff(id);
          dxl.setOperatingMode(id, OP_POSITION);
          dxl.setOperatingMode(id, OP_VELOCITY);
          dxl.torqueOn(id);
          dxl.setGoalVelocity(id, 10, UNIT_PERCENT);

          for(int i = 0; i < 3; ++i)
          {
            dxl.ledOn(id);
            delay(500);
            dxl.ledOff(id);
            delay(500);
          }

          dxl.setGoalVelocity(id, 0, UNIT_PERCENT);
          dxl.torqueOff(id);
          
          DEBUG_SERIAL.print("ID: ");
          DEBUG_SERIAL.print(id);
          DEBUG_SERIAL.print(", Model Number: ");
          DEBUG_SERIAL.println(dxl.getModelNumber(id));
          found_dynamixel++;
        }
      }
    }
  }
  
  DEBUG_SERIAL.print("Total ");
  DEBUG_SERIAL.print(found_dynamixel);
  DEBUG_SERIAL.println(" DYNAMIXEL(s) found!");
  
}

void loop() {
  // put your main code here, to run repeatedly:
}
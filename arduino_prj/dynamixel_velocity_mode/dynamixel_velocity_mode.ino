/*******************************************************************************
* Copyright 2016 ROBOTIS CO., LTD.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/

#include <DynamixelShield.h>

#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_MEGA2560)
  // this is my configuration
  #include <SoftwareSerial.h>
  SoftwareSerial soft_serial(7, 8); // DYNAMIXELShield UART RX/TX
  #define DEBUG_SERIAL soft_serial
#elif defined(ARDUINO_SAM_DUE) || defined(ARDUINO_SAM_ZERO)
  #define DEBUG_SERIAL SerialUSB
#else
  #define DEBUG_SERIAL Serial
#endif

const uint8_t DXL_ID = 1;
const float DXL_PROTOCOL_VERSION = 2.0;


DynamixelShield dxl;

//This namespace is required to use Control table item names
using namespace ControlTableItem;

void setup() {
  // put your setup code here, to run once:
  
  // For Uno, Nano, Mini, and Mega, use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(115200);
  
  // Set Port baudrate to 57600bps. This has to match with DYNAMIXEL baudrate.
  //dxl.begin(57600);
  dxl.begin(1000000); // I use 1 Mbps for my XL430s
  

  // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);


  for(int i=0;i<255;++i)
  {
    int ret = dxl.ping(i);
    DEBUG_SERIAL.print("ping ");
    DEBUG_SERIAL.print(i);
    DEBUG_SERIAL.print(": ");
    DEBUG_SERIAL.println(ret);
  }

  DEBUG_SERIAL.print("setting motor id to: ");
  DEBUG_SERIAL.println(DXL_ID);

  // Get DYNAMIXEL information
  int ret = dxl.ping(DXL_ID);
  DEBUG_SERIAL.print("ping: ");
  DEBUG_SERIAL.println(ret);

    // Get DYNAMIXEL information
  ret = dxl.scan();
  DEBUG_SERIAL.print("scan: ");
  DEBUG_SERIAL.println(ret);


  // Turn off torque when configuring items in EEPROM area
  ret = dxl.torqueOff(DXL_ID);
  DEBUG_SERIAL.print("torque off: ");
  DEBUG_SERIAL.println(ret);
  dxl.setOperatingMode(DXL_ID, OP_VELOCITY);
  ret = dxl.torqueOn(DXL_ID);
  DEBUG_SERIAL.print("torque on: ");
  DEBUG_SERIAL.println(ret);
}

void loop() {
  // put your main code here, to run repeatedly:
  
  // Please refer to e-Manual(http://emanual.robotis.com) for available range of value. 
  // Set Goal Velocity using RAW unit
  dxl.setGoalVelocity(DXL_ID, 200);
  delay(1000);
  // Print present velocity
  DEBUG_SERIAL.print("Present Velocity(raw) : ");
  DEBUG_SERIAL.println(dxl.getPresentVelocity(DXL_ID));
  delay(1000);

  // Set Goal Velocity using RPM
  dxl.setGoalVelocity(DXL_ID, 25.8, UNIT_RPM);
  delay(1000);
  DEBUG_SERIAL.print("Present Velocity(rpm) : ");
  DEBUG_SERIAL.println(dxl.getPresentVelocity(DXL_ID, UNIT_RPM));
  delay(1000);

  // Set Goal Velocity using percentage (-100.0 [%] ~ 100.0 [%])
  dxl.setGoalVelocity(DXL_ID, -10.2, UNIT_PERCENT);
  delay(1000);
  DEBUG_SERIAL.print("Present Velocity(ratio) : ");
  DEBUG_SERIAL.println(dxl.getPresentVelocity(DXL_ID, UNIT_PERCENT));
  delay(1000);
}

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
  const int32_t baud[MAX_BAUD] = {57600, 115200, 1000000, 2000000, 3000000}; //  on my board it stuck at 2M id0
#else
  #define MAX_BAUD 4
  const int32_t baud[MAX_BAUD] = {9600, 57600, 115200, 1000000}; // default for 430 is 57600
#endif

// config for misbkit:
#define DXL_DIR_PIN 4
// protocol: 1.0
// baudrate: 57600

#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C * pLcd = NULL;
bool i2CAddrTest(uint8_t addr) 
{
    Wire.begin( 23, 22 ); // DATA, CLOCK for Feather 32
    Wire.beginTransmission( addr );
    if( Wire.endTransmission() == 0 ) 
    {
        return true;
    }
    return false;
}
void setup_lcd( const char * init_msg = NULL )
{
  uint8_t i2cAddr = 0x3F;
  if( ! i2CAddrTest( i2cAddr ) )
  {
    i2cAddr = 0x27;
  }

  Serial.print( "DBG: Using LCD at I2C Addr: 0x" ); Serial.print( i2cAddr, HEX ); Serial.print( ", found: " ); Serial.println( i2CAddrTest( i2cAddr ) );

  pLcd = new LiquidCrystal_I2C( i2cAddr, 20, 4 ); // 0x3F sur la version de base, 0x27 sur la version oversized
  pLcd->init();                // initialize the lcd
  pLcd->backlight();           // Turn on backlight // sans eclairage on voit rien...
  pLcd->setCursor( 0, 0 );
  if( init_msg != NULL )
  {
    pLcd->print( init_msg );
  }
  pLcd->print( "setup_lcd finished" );
}


Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

// default value, will be changed by last found one during the scan
int nMotorId      = 1;
int nNumProtocol  = 1;
int32_t nBaudRate = 57600;




void setup() {
  // put your setup code here, to run once:
  int8_t index = 0;
  int8_t found_dynamixel = 0;
  
  // Use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(115200);   //set debugging port baudrate to 115200bps
  while(!DEBUG_SERIAL);         //Wait until the serial port is opened

  DEBUG_SERIAL.println( "misbkit_dynamix v0.61" );

  DEBUG_SERIAL.println( "INF: Setup starting..." );

  setup_lcd( "misbkit_dynamixel.ino v0.61" );

  DEBUG_SERIAL.println( "INF: Scanning..." );

  DEBUG_SERIAL.print( "Serial: " );
  DEBUG_SERIAL.println( Serial );

//  DEBUG_SERIAL.print("Serial1: ");
//  DEBUG_SERIAL.println(Serial1);

  DEBUG_SERIAL.print("DXL_SERIAL: ");
  DEBUG_SERIAL.println(DXL_SERIAL);


  DEBUG_SERIAL.print("DXL_DIR_PIN: ");
  DEBUG_SERIAL.println(DXL_DIR_PIN);
  
  for(int8_t protocol = 1; protocol < 3; protocol++) {
    // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.

    dxl.setPortProtocolVersion((float)protocol);
    DEBUG_SERIAL.print("SCAN PROTOCOL ");
    DEBUG_SERIAL.println(protocol);
    
    for(index = 0; index < MAX_BAUD; index++) {
      // Set Port baudrate.
      DEBUG_SERIAL.print("SCAN BAUDRATE ");
      DEBUG_SERIAL.println(baud[index]);
      dxl.begin(baud[index]);
      for(int id = 0; id < DXL_BROADCAST_ID; id++) 
      {
        // iterate until all ID in each baudrate is scanned.
        // DEBUG_SERIAL.println(id);
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

          nNumProtocol = protocol;
          nBaudRate = baud[index];
          nMotorId = id;
          
          found_dynamixel++;
        }
      }
    }
  }
  
  DEBUG_SERIAL.print("Total ");
  DEBUG_SERIAL.print(found_dynamixel);
  DEBUG_SERIAL.println(" DYNAMIXEL(s) found!");


  // set found one
  DEBUG_SERIAL.println( "INF: Will now use:" );
  DEBUG_SERIAL.print( "INF: protocol: " ); DEBUG_SERIAL.println( nNumProtocol );
  DEBUG_SERIAL.print( "INF: baudrate: " ); DEBUG_SERIAL.println( nBaudRate );
  DEBUG_SERIAL.print( "INF: nMotorId: " ); DEBUG_SERIAL.println( nMotorId );

  dxl.setPortProtocolVersion((float)nNumProtocol);
  dxl.begin(nBaudRate);

  DEBUG_SERIAL.println("INF: setup finished");
  
}

void loop() 
{
  debug_on_lcd();
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
}


void debug_on_lcd(void)
{
  
}
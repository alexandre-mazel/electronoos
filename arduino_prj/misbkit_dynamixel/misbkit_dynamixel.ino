/* 
  Copyright 2025, Alexandre Mazel. 


*/

/*

Current "normal" warning: 

WARNING: library LiquidCrystal I2C claims to run on avr architecture(s) and may be incompatible with your current board which runs on esp32 architecture(s).

C:\Users\alexa\dev\git\electronoos\arduino_prj\misbkit_dynamixel\misbkit_dynamixel.ino:34: warning: "DXL_DIR_PIN" redefined
 #define DXL_DIR_PIN 4
 
In file included from C:\Users\alexa\dev\git\electronoos\arduino_prj\misbkit_dynamixel\misbkit_dynamixel.ino:13:
c:\Users\alexa\Documents\Arduino\libraries\DynamixelShield\src/DynamixelShield.h:41: note: this is the location of the previous definition
   #define DXL_DIR_PIN  2
   
   TODO: rename to MISBKIT_DXL_DIR_PIN (and test it works...)
*/

#include <DynamixelShield.h>


#define DEBUG_SERIAL Serial


#define MAX_BAUD 4
const int32_t baud[MAX_BAUD] = {9600, 57600, 115200, 1000000}; // default for 430 is 57600


// config for misbkit:
#undef  DXL_DIR_PIN
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

// print one message per line then warp (if int_val is set, it will also add this value)
int lcd_print_message_next_message = 0;
void lcd_print_message( const char * msg, int int_val = -421 )
{
  int nNbrPrinted = 0;

  pLcd->setCursor( 0,lcd_print_message_next_message );
  nNbrPrinted = pLcd->print( msg );

  
  if( int_val != -421 )
  {
    nNbrPrinted += pLcd->print( int_val );
  }

  // erase end of line:
  while( nNbrPrinted < 20 )
  {
    nNbrPrinted += pLcd->print( " " );
  }

  ++lcd_print_message_next_message;
  if( lcd_print_message_next_message > 3 )
  {
    lcd_print_message_next_message = 0;
  }
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
  if( init_msg != NULL )
  {
    lcd_print_message( init_msg );
  }
  lcd_print_message( "setup_lcd finished " );
}


Dynamixel2Arduino dxl(DXL_SERIAL, DXL_DIR_PIN);

// default value, will be changed by last found one during the scan
int nMotorId      = -1;
int nNumProtocol  = 1;      // 1
int32_t nBaudRate = 57600;  // 57600
#define NBR_MOTOR_MAX 16
int anFoundMotorIds[NBR_MOTOR_MAX];
int nNbrFoundMotor = 0;


void setup() {
  // put your setup code here, to run once:
  int8_t index = 0;
  int8_t found_dynamixel = 0;
  
  // Use UART port of DYNAMIXEL Shield to debug.
  DEBUG_SERIAL.begin(115200);   //set debugging port baudrate to 115200bps
  while(!DEBUG_SERIAL);         //Wait until the serial port is opened

  const char str_version[] = "misbkit_dynami v0.63"; // limit to 20 chars to print on the lcd

  DEBUG_SERIAL.println( str_version );

  DEBUG_SERIAL.println( "INF: Setup starting..." );

  setup_lcd( str_version );

  pLcd->setCursor( 0, 2 );
  DEBUG_SERIAL.println( "INF: Scanning..." );

  lcd_print_message( "Scanning..." );
  
  //lcd_print_message( "Testing lcd on 4 lines" );
  //lcd_print_message( "blablabla" );
  //lcd_print_message( "blablabla2" );

  DEBUG_SERIAL.print( "Serial: " );
  DEBUG_SERIAL.println( Serial );

//  DEBUG_SERIAL.print("Serial1: ");
//  DEBUG_SERIAL.println(Serial1);

  DEBUG_SERIAL.print("DXL_SERIAL: ");
  DEBUG_SERIAL.println(DXL_SERIAL);


  DEBUG_SERIAL.print("DXL_DIR_PIN: ");
  DEBUG_SERIAL.println(DXL_DIR_PIN);
  
  for( int8_t protocol = 1; protocol < 3; ++protocol ) // increase search 
  {
    // Set Port Protocol Version. This has to match with DYNAMIXEL protocol version.

    dxl.setPortProtocolVersion((float)protocol);
    DEBUG_SERIAL.print("SCAN PROTOCOL ");
    DEBUG_SERIAL.println(protocol);
    
    for(index = 0; index < MAX_BAUD; index++) {
      // Set Port baudrate.
      DEBUG_SERIAL.print("SCAN BAUDRATE ");
      DEBUG_SERIAL.println(baud[index]);
      lcd_print_message( "Testing BR: ", baud[index] );
      dxl.begin(baud[index]);
      for(int id = 0; id < DXL_BROADCAST_ID; id++) 
      {
        // iterate until all ID in each baudrate is scanned.
        // DEBUG_SERIAL.println(id);
        if(dxl.ping(id)) 
        {
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

          lcd_print_message( "Found motor id: ", id );

          nNumProtocol = protocol;
          nBaudRate = baud[index];

          anFoundMotorIds[nNbrFoundMotor] = id;
          ++nNbrFoundMotor;
        } // dxl.ping
      }
    }
  }
  
  DEBUG_SERIAL.print( "Total " );
  DEBUG_SERIAL.print( nNbrFoundMotor );
  DEBUG_SERIAL.println( " DYNAMIXEL(s) found!" );

  lcd_print_message( "Nbr Motor found: ", nNbrFoundMotor );
  delay( 2000 ); // time to read message


  // set found one
  // DEBUG_SERIAL.println( "INF: Will now use:" );
  // DEBUG_SERIAL.print( "INF: protocol: " ); DEBUG_SERIAL.println( nNumProtocol );
  // DEBUG_SERIAL.print( "INF: baudrate: " ); DEBUG_SERIAL.println( nBaudRate );
  // DEBUG_SERIAL.print( "INF: nMotorId: " ); DEBUG_SERIAL.println( nMotorId );

  dxl.setPortProtocolVersion((float)nNumProtocol);
  dxl.begin(nBaudRate);


  if( 0 )
  {
    // Tested and working code to rename a servo id
    if( nNbrFoundMotor > 0 )
    {
      int nSrc = 6;
      int nDst = 9;
      lcd_print_message( "WARNING: in 5 sec" );
      lcd_print_message( "Write motor ID: ", nSrc );
      lcd_print_message( "To ID: ", nDst );
      delay( 6000 );
      dxl.setID( nSrc, nDst );
      
      
      lcd_print_message( "WRITED !!!" );
    }
  }

  if( 1 )
  {
    // Tested and working code to rename a servo id
    if( nNbrFoundMotor > 0 )
    {
      int nID = 17;
      int nNewBaudrate = 57600;

      lcd_print_message( "WARNING: in 5 sec" );
      lcd_print_message( "Change motor ID: ", nID );
      lcd_print_message( "To BR: ", nNewBaudrate );

      for(int i = 0; i < 12; ++i)
      {
        dxl.ledOn(nID);
        delay(250);
        dxl.ledOff(nID);
        delay(250);
      }
      
      //delay( 3000 );
      dxl.setBaudrate( nID, nNewBaudrate );
      
      
      lcd_print_message( "WRITED !!!" );
    }
  }

  DEBUG_SERIAL.println( "INF: setup finished" );
  
} // setup

void loop() 
{
  for( int nNumMotor = 0; nNumMotor < nNbrFoundMotor; ++nNumMotor )
  {
    nMotorId = anFoundMotorIds[nNumMotor];
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

  if( 1 )
  {
    // all in one fast ping pong
    for( int nNumMotor = 0; nNumMotor < nNbrFoundMotor; ++nNumMotor )
    {
      nMotorId = anFoundMotorIds[nNumMotor];
      dxl.torqueOff(nMotorId);
      dxl.setOperatingMode(nMotorId, OP_VELOCITY);
      dxl.setGoalVelocity(nMotorId, 0, UNIT_PERCENT); // sinon il peut y avoir un reste d'une autre commande, et le temps d'envoyer a tout les moteurs certains commencent a tourner dans l'autre sens (reste du coup d'avant) (bof la difference n'est pas claire)
      dxl.torqueOn(nMotorId);
    }
    for( int nNumMotor = 0; nNumMotor < nNbrFoundMotor; ++nNumMotor )
    {
      nMotorId = anFoundMotorIds[nNumMotor];
      dxl.setGoalVelocity(nMotorId, 100, UNIT_PERCENT);
    }
    delay(2000);
    for( int nNumMotor = 0; nNumMotor < nNbrFoundMotor; ++nNumMotor )
    {
      nMotorId = anFoundMotorIds[nNumMotor];
      dxl.setGoalVelocity(nMotorId, 1023, UNIT_RAW);
    }
    delay(2000);
    for( int nNumMotor = 0; nNumMotor < nNbrFoundMotor; ++nNumMotor )
    {
      nMotorId = anFoundMotorIds[nNumMotor];
      dxl.torqueOff(nMotorId);
    }
  }
} // loop


void debug_on_lcd(void)
{
  pLcd->clear();
  pLcd->setCursor( 0, 0 );
  pLcd->print( "Protocol: " ); pLcd->print( nNumProtocol );
  pLcd->setCursor( 0, 1 );
  pLcd->print( "BaudRate: " ); pLcd->print( nBaudRate );
  pLcd->setCursor( 0, 2 );
  pLcd->print( "MotorId: " ); pLcd->print( nMotorId );
}
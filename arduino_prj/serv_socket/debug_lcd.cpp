#include "debug_lcd.hpp"
#include <LiquidCrystal_I2C.h>
#include <arduino.h> // for Serial

LiquidCrystal_I2C * pLcd = NULL;

bool i2CAddrTest( uint8_t addr ) 
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
void lcd_print_message( const char * msg, int int_val )
{
  int nNbrPrinted = 0;

  pLcd->setCursor( 0,lcd_print_message_next_message );
  nNbrPrinted = pLcd->print( msg );

  Serial.print( "LCD: " ); Serial.print( msg );

  
  if( int_val != -421 )
  {
    nNbrPrinted += pLcd->print( int_val );
    Serial.print( int_val );
  }
  Serial.println( "" );

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

void lcd_print_message( const char * msg, const char * msg2 )
{
  // BEURK: un gros copié/collé!
  int nNbrPrinted = 0;

  pLcd->setCursor( 0,lcd_print_message_next_message );
  nNbrPrinted = pLcd->print( msg );

  Serial.print( "LCD: " ); Serial.print( msg );

  
  if( msg2 != NULL )
  {
    nNbrPrinted += pLcd->print( msg2 );
    Serial.print( msg2 );
  }
  Serial.println( "" );

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

void setup_lcd( const char * init_msg )
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
  lcd_print_message( "setup_lcd finished " );
  if( init_msg != NULL )
  {
    lcd_print_message( init_msg );
  }
}
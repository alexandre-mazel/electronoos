#ifndef __DEBUG_LCD_H__
#define __DEBUG_LCD_H__

#include <stddef.h> // for NULL

// about this WARNING: library LiquidCrystal I2C claims to run on avr architecture(s) and may be incompatible with your current board which runs on esp32 architecture(s).
// In  Arduino/libraries/LiquidCrystal_I2C library, library.properties, change the architecture line from "architecture=avr" to "architecture=avr,esp32"

void setup_lcd( const char * init_msg = NULL ); // init lcd and output an optionnal init message
void lcd_print_message( const char * msg, int int_val = -421 ); // output a message and an optionnal value
void lcd_print_message( const char * msg, const char * msg2 ); // output a message and an optionnal other message

#endif
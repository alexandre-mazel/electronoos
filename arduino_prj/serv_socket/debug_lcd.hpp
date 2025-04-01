#ifndef __DEBUG_LCD_H__
#define __DEBUG_LCD_H__

#include <stddef.h> // for NULL

void setup_lcd( const char * init_msg = NULL ); // init lcd and output an optionnal init message
void lcd_print_message( const char * msg, int int_val = -421 ); // output a message and an optionnal value

#endif
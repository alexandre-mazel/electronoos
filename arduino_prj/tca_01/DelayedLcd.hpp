#ifndef DELAYED_LCD_H
#define DELAYED_LCD_H

#include <Print.h>

#define BUF_MAX_SIZE (20*4)


class DelayedLcd
{
    /*
      The idea is to render on the lcd screen one char per one char: 
        once a full screen has been sent by user, 
        one char will be wrotten.
        home and following  chars are rejected since the current screen hasn't been rendered
    */

    public:
        
        DelayedLcd(int row, int column, Print* pHwLcd); // pHwLcd is a pointer on the real lcd to send chars
        void home(void);
        void print(const char * s);
        void print(float f,int precision = 2 );
        void print(int n);
        void update(void);

        void init(void);
        void backlight(void){};

        void printState();

    private:
        void _resetPage(); // end of page reached, ready for a new one

    private:
      Print * pHwLcd_;
      int     row_;
      int     column_;
      char    buf_[BUF_MAX_SIZE];       // store current char to write
      int     nNextAdd_;        // next place to add char
      int     nNextDraw_;       // next char to draw on lcd // -1 => must go to zero
      int     bInReject_;       // Are we rejecting ?
        
}; // class DelayedLcd




#endif DELAYED_LCD_H
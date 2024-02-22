#include "delayedlcd.hpp"
#include "hd44780.h"

DelayedLcd::DelayedLcd(int row, int column, Print * pHwLcd_)
  : pHwLcd_( pHwLcd_ )
  , row_( row )
  , column_( column )
  , nNextDraw_( 0 )
  , nNextAdd_( 0 )
  , bInReject_( 0 )
{
}

void DelayedLcd::init(void)
{
  static_cast<hd44780*>(pHwLcd_)->init();
}

void DelayedLcd::home(void)
{
  if( nNextAdd_ > nNextDraw_ )
  {
    bInReject_ = 1;
  }
}

void DelayedLcd::printState()
{
  Serial.print("nNextAdd_: ");
  Serial.println(nNextAdd_);

  Serial.print("nNextDraw_: ");
  Serial.println(nNextDraw_);
}

void DelayedLcd::print(const char * s)
{
  Serial.println("DBG: DelayedLcd.update");
  printState();
  if( bInReject_ )
  {
    return;
  }

  int len = strlen(s);

  memcpy(s,buf_+nNextAdd_,len);
  nNextAdd_ += len;
  
}

void DelayedLcd::update(void)
{
  Serial.println("DBG: DelayedLcd.update");
  static char s[2] = "?";
  if( nNextDraw_ >= nNextAdd_ )
  {
     // nothing to draw
    Serial.println("DBG: DelayedLcd.update: nothing to draw");
    return;
  }
  //s[0] = buf_[nNextDraw_];
  
  pHwLcd_->print(s);
  ++nNextDraw_;
  if( nNextDraw_ >= nNextAdd_ && bInReject_ )
  {
    // first time, reach end of buffer, ready to get new one
    bInReject_ = 0;
    nNextAdd_ = 0;
  }
}
 

#include "delayedlcd.hpp"

#include "hd44780.h" // when changing implementation of print need to change all static_cast, beurk!

//#define OUTPUT_DEBUG

#ifdef  OUTPUT_DEBUG
  #define DEBUG(x) Serial.print(x)
  #define DEBUGLN(x) Serial.println(x)
  #else
  #define DEBUG(x) /* */
  #define DEBUGLN(x) /* */
#endif // OUTPUT_DEBUG

void DelayedLcd::printState()
{
#ifdef  OUTPUT_DEBUG
  Serial.print("buf_: ");
  Serial.println(buf_);

  Serial.print("nNextAdd_: ");
  Serial.println(nNextAdd_);

  Serial.print("nNextDraw_: ");
  Serial.println(nNextDraw_);

  Serial.print("bInReject_: ");
  Serial.println(bInReject_);
#endif // OUTPUT_DEBUG
}

DelayedLcd::DelayedLcd(int row, int column, Print * pHwLcd_)
  : pHwLcd_( pHwLcd_ )
  , row_( row )
  , column_( column )
  , nNextAdd_( 0 )
  , nNextDraw_( -1 )
  , bInReject_( 0 )
{
  buf_[BUF_MAX_SIZE-1] = '\0';
  _resetPage();
}

void DelayedLcd::_resetPage()
{
    bInReject_ = 0;
    nNextAdd_ = 0;
    nNextDraw_ = -1;
}

void DelayedLcd::init(void)
{
  static_cast<hd44780*>(pHwLcd_)->init();
}

void DelayedLcd::home(void)
{
  DEBUGLN("DBG: DelayedLcd.home");
  printState();

  if( nNextAdd_ > nNextDraw_ && (nNextDraw_ != -1 || nNextAdd_ != 0 ) )
  {
    // on n'a pas fini de dessiner l'ecran actuel
    bInReject_ = 1;
  }

}


void DelayedLcd::print(const char * s)
{
  DEBUGLN("DBG: DelayedLcd.print");
  DEBUG("DBG: printing: ");
  DEBUGLN(s);

  printState();
  if( bInReject_ )
  {
    return;
  }

  int len = strlen(s);

  if( nNextAdd_ >= BUF_MAX_SIZE )
  {
    DEBUGLN("WRN: Too much char");
    return;
  }

  if(nNextAdd_+len >= BUF_MAX_SIZE)
  {
    len = BUF_MAX_SIZE-nNextAdd_;
  }

  memcpy(buf_+nNextAdd_,s,len);
  nNextAdd_ += len;
}

void DelayedLcd::print(float f, int precision)
{
  static char buf[16];
  //snprintf(buf, 15,"%5.2f", (float)f);
  dtostrf(f,3,precision,buf); 
  print(buf);
}
void DelayedLcd::print(int n)
{
  static char buf[16];
  snprintf(buf, 15,"%d", n);
  print(buf);
}

void DelayedLcd::update(void)
{
  DEBUGLN("DBG: DelayedLcd.update");
  printState();

  static char s[2] = "?";
  if( nNextDraw_ >= nNextAdd_ )
  {
     // nothing to draw
    DEBUGLN("DBG: DelayedLcd.update: nothing to draw");
    return;
  }

  if(nNextDraw_ == -1 )
  {
    static_cast<hd44780*>(pHwLcd_)->home();
    nNextDraw_ = 0;
    return;
  }
  
  s[0] = buf_[nNextDraw_];
  
  pHwLcd_->print(s);
  ++nNextDraw_;
  if( nNextDraw_ >= nNextAdd_ )
  {
    // first time, reach end of buffer, ready to get new one
    _resetPage();
  }
}
 

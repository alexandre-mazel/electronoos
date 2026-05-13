#include "historic.h"
#include <Arduino.h> // for malloc

// here all device that will need to be used by this method
#include "oled.h"

Historic::Historic(int w)
{
  w_ = w;
  values_ = (int*)malloc(w_*sizeof(int));
  n_ = 0;
}

void Historic::append(int v)
{
  if(n_+1>=w_)
  {
    // eat one value
    --n_;
    memcpy(values_,values_+1,n_*sizeof(int));
  }
  values_[n_] = v;
  ++n_;
}

void Historic::drawGraphicOled( int x, int y, void * pOledObject, int hmax )
{
  //Serial.print("in disp, histo len: " );
  //Serial.println(n_);

  OLED * pOled = (OLED*) pOledObject;

  int valmax = 4; // min value
  for( int i = 0; i < n_; ++i )
  {
    if( valmax < values_[i] )
    {
      valmax = values_[i];
    } 
  }

  //Serial.print("valmax: " );
  //Serial.println(valmax);

  int xval = x;
  for( int i = 0; i < n_; ++i )
  { 
    int yval = y - (values_[i]*hmax/valmax);
    /*
    Serial.print( "val: " );
    Serial.print( values_[i] );
    Serial.print( ", yval: " );
    Serial.println( yval );
    */
    pOled->draw_line(xval,y-hmax,xval,y,OLED::BLACK); // efface le previous // 120 lines with hmax 32 => 20ms (arduino mega)
    //pOled->draw_pixel(xval,yval,OLED::WHITE); // dessine le point
    pOled->draw_line(xval,yval,xval,y,OLED::WHITE); // dessine une ligne pleine // 120 lines with constant value => 21ms (white is slighly longer?)
    ++xval;
  }

}
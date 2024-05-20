#include "optimal_text_renderer.h"

#include <string.h>
#include <MCUFRIEND_kbv.h>

//#define ALLOW_DESTRUCTION

OptimalTextRenderer::OptimalTextRenderer(int colorBackground, int colorText, int nSizeText, int x, int y, int nNbrCharMax = 16 )
  : colorBackground_  (colorBackground)
  , colorText_        ( colorText )
  , nSizeText_        (nSizeText)
  , x_                ( x )
  , y_                ( y )
  , nNbrCharMax_      ( nNbrCharMax )
#ifdef ALLOW_DESTRUCTION
  , lastRenderedText_ ( 0 )
#endif
{
  lastRenderedText_ = new char[nNbrCharMax+1];

}

OptimalTextRenderer::~OptimalTextRenderer()
{
#ifdef ALLOW_DESTRUCTION
  delete[] lastRenderedText_;
  lastRenderedText_ = 0;
#endif
}

void OptimalTextRenderer::render( MCUFRIEND_kbv * pTft, const char * txt )
{
  if(1 && strcmp(lastRenderedText_,txt) == 0)
    return;
  
  //Serial.print("OptimalTextRenderer: rendering: "); Serial.println(txt);


  // version no optim, just to test rendering
  /*
  pTft->fillRect( x_, y_, nSizeText_*6*strlen(txt), nSizeText_*7, colorBackground_ );
  pTft->setTextSize(nSizeText_);
  pTft->setTextColor(colorText_);
  pTft->setCursor(x_,y_);
  pTft->print(txt);
  */

  pTft->setTextSize(nSizeText_);
  pTft->setTextColor(colorText_);

  char * p = lastRenderedText_;
  const char * ptxt = txt;
  int num_char = 0;
  int xcur = x_;
  int nSizeChar = nSizeText_*6;
  while(*ptxt)
  {
    if( (*p) != (*txt) )
    {
      // render new char
      pTft->fillRect( xcur, y_, nSizeChar, nSizeText_*7, colorBackground_ );
      pTft->setCursor(xcur,y_);
      pTft->print(*ptxt);
    }
    xcur += nSizeChar;
    ++ptxt;
    ++p;
  }
  strcpy(lastRenderedText_,txt);
}
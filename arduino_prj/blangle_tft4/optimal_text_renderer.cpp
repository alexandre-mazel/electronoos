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

OptimalTextRenderer::render( MCUFRIEND_kbv * pTft, const char * txt )
{
  if(strcmp(lastRenderedText_,txt) == 0)
    return;
  
  // version no optim, just to test rendering
  pTft->setTextSize(nSizeText_);
  pTft->setTextColor(colorText_);
  pTft->setCursor(x_,y_);
  pTft->print(txt);
  strcpy(lastRenderedText_,txt);
}
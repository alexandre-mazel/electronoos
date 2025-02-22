#include "Ai_WS2811.h"

void hueToRGB( int nHue, uint8_t * prRet, uint8_t * pgRet, uint8_t * pbRet )
{
  //this is the algorithm to convert from RGB to HSV
  double r=0; 
  double g=0; 
  double b=0;

  double hf=nHue/42.5; // Not /60 as range is _not_ 0-360

  int i=(int)floor(nHue/42.5);
  double f = nHue/42.5 - i;
  double qv = 1 - f;
  double tv = f;

  switch (i)
  {
  case 0: 
    r = 1;
    g = tv;
    break;
  case 1: 
    r = qv;
    g = 1;
    break;
  case 2: 
    g = 1;
    b = tv;
    break;
  case 3: 
    g = qv;
    b = 1;
    break;
  case 4:
    r = tv;
    b = 1;
    break;
  case 5: 
    r = 1;
    b = qv;
    break;
  }
  
  (*prRet) = constrain((int)255*r,0,255);
  (*pgRet) = constrain((int)255*g,0,255);  
  (*pbRet) = constrain((int)255*b,0,255);  
}


void Ai_WS2811::init(uint8_t pin, uint16_t nPixels) 
{
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
  m_nLeds = nPixels * 3; 
  m_nCounter = 0; 
  m_pData = (unsigned char*)malloc(m_nLeds); 
  memset(m_pData,0,m_nLeds);
  m_pDataEnd = m_pData + m_nLeds;
  if( pin == 53 )
  {
    m_nNumBit = 0;
  }
  else if( pin == 52 )
  {
    m_nNumBit = 1;
  }  
  else if( pin == 51 )
  {
    m_nNumBit = 2;
  }    
  else if( pin == 50 )
  {
    m_nNumBit = 3;
  } 
  m_nDimCoef = 1;
   
}

void Ai_WS2811::setDim( const int nDimCoef )
{
  m_nDimCoef = nDimCoef;
}

void Ai_WS2811::applyDim( void )
{
  if( m_nDimCoef == 1 )
  {
    return;
  }
  register byte *p = m_pData;
  register byte *e = m_pDataEnd;
  while(p != e) 
  { 
     (*p) /= m_nDimCoef; ++p;
   }
}

void Ai_WS2811::setColor(unsigned char r,unsigned char g,unsigned char b)
{
  /*
  Serial.print("setColor " );
  Serial.print(r);
  Serial.print( ", " );
  Serial.print(g);
  Serial.print( ", " );
  Serial.print(b);
  Serial.println( "" );
  */

  register byte *p = m_pData;
  register byte *e = m_pDataEnd;
  while(p != e) 
  { 
     *p++ = g;
     *p++ = r;
     *p++ = b;
  }  
  sendLedData();
}


void Ai_WS2811::setHue(uint8_t nNumPixel, int nHue)
{
  struct CRGB * leds = (struct CRGB *)m_pData;
  uint8_t r, g, b;
  hueToRGB( nHue, &r, &g, &b );
  leds[nNumPixel].r = constrain((int)255*r,0,255);
  leds[nNumPixel].g = constrain((int)255*g,0,255);
  leds[nNumPixel].b = constrain((int)255*b,0,255);
}

void Ai_WS2811::setVumeter( int nValue,int bR, int bG, int bB )
{
  int nNbrPixel = m_nLeds/3;
  int nNbrValuePerPixel = 10000/nNbrPixel;
  int nNbrPixelToLighten = nValue / nNbrValuePerPixel;
  int nNbrRemaining = nValue - (nNbrPixelToLighten * nNbrValuePerPixel);
  
  nNbrRemaining = map( nNbrRemaining, 0, nNbrValuePerPixel, 0, 255 );
  struct CRGB * leds = (struct CRGB *)m_pData;
  int i;
  for( i = 0; i < nNbrPixelToLighten; ++i )
  {
    if( bR ) leds[i].r = 255; else leds[i].r = 0;
    if( bG ) leds[i].g = 255; else leds[i].g = 0;
    if( bB ) leds[i].b = 255; else leds[i].b = 0;
  }
  if( i < nNbrPixel )
  {
    if( bR ) leds[i].r = nNbrRemaining; else leds[i].r = 0;
    if( bG ) leds[i].g = nNbrRemaining; else leds[i].g = 0;
    if( bB ) leds[i].b = nNbrRemaining; else leds[i].b = 0;
    ++i;
  }
  for(; i < nNbrPixel; ++i )
  {
    leds[i].r = 0;
    leds[i].g = 0;
    leds[i].b = 0;    
  }
  sendLedData();
}

void Ai_WS2811::setOnlyOne( unsigned int nIdx, uint8_t r, uint8_t g, uint8_t b )
{
  int nNbrPixel = m_nLeds/3;  
  struct CRGB * leds = (struct CRGB *)m_pData;
  memset( m_pData,0,m_nLeds );
  long i = (long)nIdx%10000;
  i = (long)(i*nNbrPixel)/10000;
//  Serial.print(i);
  leds[i].r = r;
  leds[i].g = g;
  leds[i].b = b;
  sendLedData();
}

void Ai_WS2811::setOneBrightOtherLow( unsigned int nNbrLeds, unsigned int nNumFirst, unsigned int nNumBright, uint8_t r, uint8_t g, uint8_t b, uint8_t rLow, uint8_t gLow, uint8_t bLow )
{
//  int nNbrPixel = m_nLeds/3;  
  struct CRGB * leds = (struct CRGB *)m_pData;
  for( unsigned int j = 0; j < nNbrLeds; ++j )
  {
    leds[j+nNumFirst].r = rLow;
    leds[j+nNumFirst].g = gLow;
    leds[j+nNumFirst].b = bLow;
  }
  if( nNumBright < nNbrLeds )
  {
    leds[nNumBright+nNumFirst].r = r;
    leds[nNumBright+nNumFirst].g = g;
    leds[nNumBright+nNumFirst].b = b;
  }
}

int Ai_WS2811::reducePixelNumber( int nNewPixelNumber )
{
  int nNewLedsNumber = nNewPixelNumber*3;
  if( m_nLeds <= nNewLedsNumber )
    return 0;
    
  m_nLeds = nNewLedsNumber;
  m_pDataEnd = m_pData + m_nLeds;
  return 1;
}



void Ai_WS2811::sendLedData(void)
{
  applyDim();
  cli();
  register byte *p = m_pData;
  register byte *e = m_pDataEnd;
  volatile uint8_t b;
  while(p != e) 
  { 
    b   = *p++;    // Current byte value
    byte i=8;
    do {
      if ((b&0x80)==0) {
        // Send a '0'
        if (F_CPU==16000000L) {
          LED_PIN=LED_BIT;NOP;// Hi (start)
          NOP;NOP;            // Hi
          LED_PIN=LED_BIT;NOP;// Lo (250ns)
          NOP;NOP;            // Lo
          NOP;NOP;            // Lo (500ns)
        }   
        else if (F_CPU==8000000L) {
          LED_PIN = LED_BIT;  // Hi (start)
          NOP;                // Hi
          LED_PIN = LED_BIT;  // Lo (250ns)
          NOP;                // Lo
          NOP;                // Lo (500ns)
          NOP;                // Lo (data bit here!)  
          NOP;                // Lo (750ns)
        }   
      }   
      else {
        // Send a '1'
        if (F_CPU==16000000L) {
          LED_PIN=LED_BIT;NOP;// Hi (start)
          NOP;NOP;            // Hi
          NOP;NOP;            // Hi (250ns)
          NOP;NOP;            // Hi
          NOP;NOP;            // Hi (500ns)
          LED_PIN=LED_BIT;    // Lo (625ns)
        }   
        else if (F_CPU==8000000L) {
          LED_PIN = LED_BIT;  // Hi (start)
          NOP;                // Hi
          NOP;                // Hi (250ns)
          NOP;                // Hi
          NOP;                // Hi (500ns)
          NOP;                // Hi (data bit here!)
          LED_PIN = LED_BIT;  // Lo (750ns)
        }   
      }   
      b = b+b;
    } while (--i!=0);
  }
  sei();
}

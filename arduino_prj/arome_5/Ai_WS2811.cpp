#include "Ai_WS2811.h"

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
  Serial.print("setColor " );
  Serial.print(r);
  Serial.print( ", " );
  Serial.print(g);
  Serial.print( ", " );
  Serial.print(b);
  Serial.println( "" );

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
    if( bR ) leds[i].r = 255;
    if( bG ) leds[i].g = 255;
    if( bB ) leds[i].b = 255;    
  }
  if( i < nNbrPixel )
  {
    if( bR ) leds[i].r = nNbrRemaining;
    if( bG ) leds[i].g = nNbrRemaining;
    if( bB ) leds[i].b = nNbrRemaining;
    ++i;
  }
  for(; i < nNbrPixel; ++i )
  {
    if( bR ) leds[i].r = 0;
    if( bG ) leds[i].g = 0;
    if( bB ) leds[i].b = 0;    
  }
  sendLedData();
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

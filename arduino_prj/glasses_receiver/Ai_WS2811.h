#include <Arduino.h>
#include <util/delay.h>

// v0.67: move macro to .cpp
// v0.66: add setonlyone
// v0.65: debug setvumetre
// v0.64: add setvumetre and change dim method
// v0.63: add multi port ability
// v0.62: add setColor method
// v0.61: add CRGB struct definition
// v0.6: add dim and version !

// Assume Arduino Uno, digital pin 8 lives in Port B

class Ai_WS2811 
{
  private:
    int m_nLeds; // number of monochrome leds = 3xnbr pixel
    unsigned char m_nDataRate;
    unsigned long m_nCounter;
    unsigned char *m_pData;
    unsigned char *m_pDataEnd;
    unsigned int  m_nNumBit; // 0 => 53, 1 => 51, 2 => 52...
    unsigned int  m_nDimCoef; // set a coef to dim

  public:
    byte _r, _g, _b;
    uint8_t *led_arr;
    void init( uint8_t nNumPin, uint16_t nNbrPixel );
    void sendLedData(void);
    
    void setDim( const int nDimCoef = 2 ); // dim all leds by a coef (to avoid burning my eyes)
    
    void setColor( unsigned char r,unsigned char g,unsigned char b ); // set all color at the same time
    
    // light the vumeter
    // -nValue: [0..10000]    
    void setVumeter( int nValue, int bR = 1, int bG = 1, int bB = 1 );
    
    // set the pixel in a group and unset all the other. 
    // nIdx: an index between 0 and 10000 => the nearest pixel will be set (no interpolation) if nIdx is > 10000 => loop
    void setOnlyOne( unsigned int nIdx, uint8_t r, uint8_t g, uint8_t b );
    
    int reducePixelNumber( int nNewPixelNumber ); // reduce the pixel number to a smaller number (when inited too big or ...) return 1 if ok
    
    unsigned char *getRGBData() { return m_pData; }    
    
  private:
    void applyDim(void);
  
};

struct CRGB {
  unsigned char g;
  unsigned char r;
  unsigned char b;
} ;

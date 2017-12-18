#include <Arduino.h>
#include <util/delay.h>

// v0.72: add multi pin/port/ddr handling
// v0.71: document and debug setHue
// v0.70: setOneBrightOtherLow
// v0.66: add setonlyone
// v0.65: debug setvumetre
// v0.64: add setvumetre and change dim method
// v0.63: add multi port ability
// v0.62: add setColor method
// v0.61: add CRGB struct definition
// v0.6: add dim and version !

// Assume Arduino Uno, digital pin 8 lives in Port B
// changed also to handle Mega2560

/*
#define LED_DDR DDRB # input or output ?
#define LED_PORT PORTB # high or low?
#define LED_PIN PINB # read value
*/

#define LED_BIT _BV(m_nNumBit)
#define NOP __asm__("nop\n\t")


// transform hue to RGB
void hueToRGB( int nHue, uint8_t * prRet, uint8_t * pgRet, uint8_t * pbRet );

//on a good compilator, we should use enum...
#define BANK_A 0
#define BANK_B 1
#define BANK_C 2
#define BANK_D 3
#define BANK_E 4
#define BANK_F 5
#define BANK_G 6
#define BANK_H 7
#define BANK_I 8
#define BANK_K 9
#define BANK_L 10


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
    unsigned int  m_nNumBank; // the letter of the bank to use: BANK_x

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
    
    // Work on a segment of a length of nNbrLeds, beginning at nNumFirst
    // Set one color with others lighten with low color
    // nNumBright is relative to nNumFirst
    void setOneBrightOtherLow( unsigned int nNbrLeds, unsigned int nNumFirst, unsigned int nNumBright, uint8_t r, uint8_t g, uint8_t b, uint8_t rLow = 10, uint8_t gLow = 10, uint8_t bLow = 10 );
    
    // Set one pixel at a specific hue. Don't touch others
    void setHue( uint8_t nNumPixel, int nHue );    // nHue between 0 and 254
    
    int reducePixelNumber( int nNewPixelNumber ); // reduce the pixel number to a smaller number (when inited too big or ...) return 1 if ok
    int getPixelNumber() { return m_nLeds; }
        
    unsigned char *getRGBData() { return m_pData; }    
    
  private:
    void applyDim(void);
    
    void sendLedData_BankB(void);
    void sendLedData_BankC(void);    
    void sendLedData_BankL(void);    
  
};

struct CRGB {
  unsigned char g;
  unsigned char r;
  unsigned char b;
} ;    
 

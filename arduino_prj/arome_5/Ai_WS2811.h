#include <Arduino.h>
#include <util/delay.h>

// v0.63: add multi port ability
// v0.62: add setColor method
// v0.61: add CRGB struct definition
// v0.6: add dim and version !

// Assume Arduino Uno, digital pin 8 lives in Port B

#define LED_DDR DDRB
#define LED_PORT PORTB
#define LED_PIN PINB
#define LED_BIT _BV(m_nNumBit)
#define NOP __asm__("nop\n\t")

class Ai_WS2811 
{
  private:
    int m_nLeds;
    unsigned char m_nDataRate;
    unsigned long m_nCounter;
    unsigned char *m_pData;
    unsigned char *m_pDataEnd;
    unsigned int  m_nNumBit; // 0 => 53, 1 => 51, 2 => 52...

  public:
    byte _r, _g, _b;
    uint8_t *led_arr;
    void init(uint8_t,uint16_t);
    void sendLedData(void);
    void dim( const int nDimCoef = 2 ); // dim all leds by a coef (to avoid burning my eyes)
    void setColor(unsigned char r,unsigned char g,unsigned char b); // set all color at the same time
    unsigned char *getRGBData() { return m_pData; } 
};

struct CRGB {
  unsigned char g;
  unsigned char r;
  unsigned char b;
} ;

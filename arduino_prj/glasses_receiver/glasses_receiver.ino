#include "Ai_WS2811.h"


#define LED_DEBUG_PIN 13
#define LED_RGB_PIN 53

#define NUM_PIXELS 8
Ai_WS2811 ws2811;
struct CRGB * pLeds = NULL;

const int bDebugWithSerial = 0;


void debug_with_led( unsigned char B )
{
  // Print a long then one impulsion per byte
  digitalWrite(LED_DEBUG_PIN, HIGH);   
  delay( 1000 );
  digitalWrite(LED_DEBUG_PIN, LOW);
  delay( 100 );          
  for( int i = 0; i < 8; ++i )
  {
    if( (1<<i) & B )
    {
      digitalWrite(LED_DEBUG_PIN, HIGH);
    }
    else
    {
      digitalWrite(LED_DEBUG_PIN, LOW);
    }
    delay( 400 );
    digitalWrite(LED_DEBUG_PIN, LOW);
    delay( 100 );      
  }
}


void setLeds( unsigned char * buf )
{
  // change color to buf, with buf: "BGR" composantes in [0..127]
  if( bDebugWithSerial )
  {
    Serial.print( "INF: setLeds: " );
    Serial.print( buf[0] );
    Serial.print( ", " );
    Serial.print( buf[1] );
    Serial.print( ", " );
    Serial.print( buf[2] );  
    Serial.println( "." );
  }
  ws2811.setColor( buf[2]*2, buf[1]*2, buf[0]*2 );
}

void checkLedsRGB( void )
{
  if( bDebugWithSerial ) Serial.println( "INF: checkLedsRGB: begin..." );
  unsigned char full[] = {127, 127, 127};
  unsigned char r[] = {0, 0, 127};
  unsigned char g[] = {0, 127,  0 };
  unsigned char b[] = {127, 0, 0};  
  const int nTimeDelay = 300;
  setLeds( r );
  delay( nTimeDelay );
  setLeds( g );  
  delay( nTimeDelay );  
  setLeds( b );
  delay( nTimeDelay );  
  setLeds( full );
  delay( nTimeDelay );  
  if( bDebugWithSerial ) Serial.println( "INF: checkLedsRGB: end" );  
}

void setup()
{  
  Serial.begin(9600);
  if( bDebugWithSerial ) Serial.println( "INF: CdL: Glasses_Receiver v0.6" );
  
  pinMode(LED_DEBUG_PIN, OUTPUT);
  for( int i = 0; i < 5; ++i )
  {
    digitalWrite(LED_DEBUG_PIN, HIGH);
    delay( 100 );
    digitalWrite(LED_DEBUG_PIN, LOW);    
    delay( 200 );      
  }

  // debug_with_led( 0 );
  // debug_with_led( 0xFF );
  
  pinMode( LED_RGB_PIN, OUTPUT );
  ws2811.init(LED_RGB_PIN,NUM_PIXELS);
  pLeds = (struct CRGB*)ws2811.getRGBData();
  ws2811.setDim( 32 );  
  
  checkLedsRGB();  
}

//unsigned char nLedValue = 0;
const int nSizeBufMax = 3*4; // 3 should be enough
unsigned char buf[nSizeBufMax] = ""; 
int nSizeBuf = 0;
void loop()
{
    while(Serial.available())
    {
      unsigned char c = Serial.read();
      if( 0 ) debug_with_led( c );
      if( 0 )
      {
        if( c >= 50 )
        {
          digitalWrite(LED_DEBUG_PIN, HIGH);
          // delay(1000);
        }
        else
        {
          digitalWrite(LED_DEBUG_PIN, LOW);
        }
      }
      
      if( c == 127 ) // 127 is the end of message
      {
        // end of message        
        if( nSizeBuf == 3 )
        {
          setLeds( buf );
        }
        else
        {
          if( bDebugWithSerial ) Serial.print( "ERR: at end of buffer, buffer hasn't the right side, nSizeBuf: " );
          if( bDebugWithSerial ) Serial.println( nSizeBuf );
        }
        nSizeBuf = 0;
      }
      else
      {
        // other chars
        buf[nSizeBuf] = c; ++nSizeBuf;
        if( nSizeBuf >= nSizeBufMax )
        {
          if( bDebugWithSerial ) Serial.print( "ERR: when adding a new byte, nSizeBuf more than max: " );
          if( bDebugWithSerial ) Serial.println( nSizeBuf );
          nSizeBuf = 0;
        }
      }
      
    } // while serial available
    
  delay( 1 ); // wait a bit
} // end of loop

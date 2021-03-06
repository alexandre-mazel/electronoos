#include "Ai_WS2811.h"
#include "fonts.h"
#include "imgs.h"

#define W 14
#define H  8
#define NUM_PIXELS (W*H)
#define DATA_PIN 53 // 47 // 53
//#define BYTE unsigned char


Ai_WS2811 ws2811;

struct CRGB  *leds;

//typedef struct sCRGB CRGB; // les typedef ne fonctionnet pas du tout...
//#define CRGB struct sCRGB

//struct CRGB * leds;

void setOne( int nNum )
{
    memset( leds, 0, NUM_PIXELS*3 ); 
    leds[nNum].r = 20;
    leds[nNum].g = 20;
    leds[nNum].b = 20;    
}

void setV( int nNum, struct CRGB * prgb )
{
    memset( leds, 0, NUM_PIXELS*3 );
    for( int i = 0; i < H; ++i )
    {
      leds[i*W+nNum].r = prgb->r;
      leds[i*W+nNum].g = prgb->g;
      leds[i*W+nNum].b = prgb->b;    
    }
    ws2811.setDim(8);
    ws2811.sendLedData();    
}

void setVumeter( int nValue )
{
  // light the vumeter
  // -nValue: [0..10000]
  const int nNbrValuePerLed = 10000/NUM_PIXELS;
  int nNbrLedToLighten = nValue / nNbrValuePerLed;
  int nNbrRemaining = nValue - (nNbrLedToLighten * nNbrValuePerLed);
//  Serial.print( "nNbrValuePerLed: " );
//  Serial.print( nNbrValuePerLed, DEC );
//  Serial.print( "nNbrLedToLighten: " );
//  Serial.print( nNbrLedToLighten, DEC );
//  Serial.print( "nNbrRemaining: " );
//  Serial.println( nNbrRemaining, DEC );
  
  nNbrRemaining = map( nNbrRemaining, 0, nNbrValuePerLed, 0, 255 );
  int i;
  for( i = 0; i < nNbrLedToLighten; ++i )
  {
    leds[i].r = 255;
    leds[i].g = 255;
    leds[i].b = 255;    
  }
  if( i < NUM_PIXELS )
  {
    leds[i].r = nNbrRemaining;
    leds[i].g = nNbrRemaining;
    leds[i].b = nNbrRemaining;
    ++i;
  }
  for(; i < NUM_PIXELS; ++i )
  {
    leds[i].r = 0;
    leds[i].g = 0;
    leds[i].b = 0;    
  }
}

void drawLetter( int nNumLetter, int x, int y )
{
   // affiche une lettre a une certaine position x,y: le coin haut gauche de la lettre
   if( nNumLetter == ' ' || nNumLetter < LETTER_FIRST || ( nNumLetter - LETTER_FIRST ) >= LETTER_NBR )
     return;
     
   unsigned char * pPixSrc = &(aLetters[(nNumLetter-LETTER_FIRST)*LETTER_SIZE_X*LETTER_SIZE_Y]);
   //unsigned char * pPixSrc = aLetters;
   int pix = x+y*W;
   int nLimitX1 = -x;
   int nLimitX2 = W-x;   
   for( int j = 0; j < LETTER_SIZE_Y; ++j ) 
   {
     for( int i = 0; i < LETTER_SIZE_X; ++i )
     {
        unsigned char val = *pPixSrc;
//        Serial.println( "pix:" );
//        Serial.println( int(pPixSrc), HEX );
//        Serial.println( int(aLetters), HEX );        
//        Serial.println( val, HEX );
        if( i >= nLimitX1 && i < nLimitX2 )
        {
          leds[pix].r = val;
          leds[pix].g = val;
          leds[pix].b = val;
        }
        ++pPixSrc;
        ++pix;
     }
     pix += W-LETTER_SIZE_X;
    }
}

void drawImg( int nNumImage, int x, int y )
{
  unsigned char * pPixSrc = &aImgs[nNumImage*IMG_SIZE_Y*IMG_SIZE_X*3];
  int pix = 0;
  while(pix<NUM_PIXELS)
  {
    leds[pix].b = *pPixSrc; ++pPixSrc;
    leds[pix].g = *pPixSrc; ++pPixSrc;
    leds[pix].r = *pPixSrc; ++pPixSrc;
    ++pix;
  }
}

int nFpsCpt = 0;
unsigned long timeFpsBegin;

#define NBR_LETTER_DRAW 3
int aLetterPos[NBR_LETTER_DRAW]; // pixel of the top left
int aLetterIdx[NBR_LETTER_DRAW]; // point the letter in the message

//some initial values
void setup()
{
  ws2811.init(DATA_PIN,NUM_PIXELS);
  leds = (struct CRGB*)ws2811.getRGBData();
  Serial.begin(9600);
  //setVumeter( 10000 ); // full all led
  //setVumeter( 1250 ); // 1 led full
  setVumeter( 0 ); // 0 led
  timeFpsBegin = micros();
  for( int i = 0; i < NBR_LETTER_DRAW; ++i )
  {
    aLetterPos[i] = W+i*(LETTER_SIZE_X+1);
    aLetterIdx[i] = i;
  }
  
  //ws2811.setDim(16);

}

int nCpt = 0;
int bPrevLighten = false;
int nCptHidden = 0;
unsigned long timeLast = 0;
int nCptFadeOut = -1;

int nBlobX = W/2;
int nBlobY = H/2;
int nBlobDX = 1;
int nBlobDY = 1;
void loop()
{

/*  
  for( int i=0; i < NUM_PIXELS; ++i )
  {
    setOne(i);
    ws2811.sendLedData();
  }
*/

  CRGB rgb;
  getHue( nCpt%256, &rgb);


/*
  for( int i = 0; i < W; ++i )
  {
    setV(i, &rgb );
    ws2811.dim(4);
    ws2811.sendLedData();    
    delay(20);
  }
  for( int i = W-2; i > 0; --i )
  {
    setV(i, &rgb);
    drawLetter( 'A', 0, 0 );
    ws2811.dim(4);
    ws2811.sendLedData();
    
    delay(20);
  }
 */

/* 
  //Serial.println( "AAAAAAAAA" );
  for( int i = -LETTER_SIZE_X+1; i < W; ++i )
  {
    memset( leds, 0, NUM_PIXELS*3 );
    drawLetter( LETTER_FIRST+(nCpt%LETTER_NBR), i, 0 );
    ws2811.dim(16);
    ws2811.sendLedData();
    delay(50);
//    break;
  }
  */

  //char szToWrite[] = "<<<Factory Rulez>>>";
  //char szToWrite[] = "- Un jour un truc 2016 !!! -"; // => timeout!
  //char szToWrite[] = "[Un jour un truc 2016] ";
  char szToWrite[] = " << O' Chateau  >>";
  int nLenMessage = sizeof(szToWrite)-1;

  /*
  
  int nIdxCurLetter = nCpt/(W+LETTER_SIZE_X-1)*2;
  
  memset( leds, 0, NUM_PIXELS*3 );
  Serial.println( szToWrite[nIdxCurLetter%nLenMessage] );
  int nX = ((-nCpt)%(W+LETTER_SIZE_X-1))-LETTER_SIZE_X+1+W+6;
  Serial.println( nX );  
  drawLetter( szToWrite[nIdxCurLetter%nLenMessage], nX, 0 );
  drawLetter( szToWrite[(nIdxCurLetter+1)%nLenMessage], nX+9, 0 );
  drawLetter( szToWrite[(nIdxCurLetter+2)%nLenMessage], nX+9, 0 );  
  ws2811.dim(16);
  ws2811.sendLedData();
  delay(100);
  */
  if( 0 )
  {
    memset( leds, 0, NUM_PIXELS*3 );
  
    for( int i = 0; i < NBR_LETTER_DRAW; ++i )
    {
      drawLetter( szToWrite[aLetterIdx[i]%nLenMessage], aLetterPos[i], 0 );      
      --aLetterPos[i];
      if( aLetterPos[i] < -LETTER_SIZE_X )
      {
        aLetterPos[i] += 3*(LETTER_SIZE_X+1);
        aLetterIdx[i] += 3;      
      }    
    }    
    ws2811.sendLedData();
    delay(40);
  }
  
  if( 0 )
  {
    drawImg( (nCpt/40)%IMG_NBR, 0, 0);
    ws2811.sendLedData();
    delay(40);    
  }
  
  if( 1 )
  {
    // we will render image, directly in aImgs (in BGR)
    memset( aImgs, 0, NUM_PIXELS*3 );    
    int x = nBlobX;
    int y = nBlobY;
    int nSize = 1;
    int nMaxDist = nSize+1;
    CRGB hue;
    getHue( nCpt%256,&hue );
    for( int j = -nSize; j <= nSize; ++j )
    {
      for( int i = -nSize; i <= nSize; ++i )
      {
        if( x+i >= 0 && x+i < W && y+j >= 0 && y+j < H )
        {
          int pix = (x+i+(y+j)*W)*3;
          float d = sqrt((i)*(i)+(j)*(j));
          int lum = 255;
          if( d != 0 )
            lum = ((nMaxDist-d)*lum)/nMaxDist;
            if( lum < 0 ) lum = 0;
            
//          Serial.print( lum );
//          Serial.print( " " );

//          getHue( nCpt%256,(CRGB*)&aImgs[pix+0] ); 
//          aImgs[pix+0] = (aImgs[pix+0]*lum)/255;
//          aImgs[pix+1] = (aImgs[pix+1]*lum)/255;
//          aImgs[pix+2] = (aImgs[pix+2]*lum)/255;
//            if( hue.b > 128 ) aImgs[pix+0] = lum;
//            if( hue.g > 128 ) aImgs[pix+1] = lum;
//            if( hue.r > 128 ) aImgs[pix+2] = lum;            
            aImgs[pix+0] = lum*hue.b/255;
            aImgs[pix+1] = lum*hue.g/255;
            aImgs[pix+2] = lum*hue.r/255;

        }
      }
//      Serial.println();  
    }
     
    nBlobX += nBlobDX;
    if( nBlobX+nSize >= W ) nBlobDX = -1;
    if( nBlobX-nSize < 0 ) nBlobDX = 1;
   
    nBlobY += nBlobDY;
    if( nBlobY+nSize >= H ) nBlobDY = -1;
    if( nBlobY-nSize < 0 ) nBlobDY = 1;
    
    
    drawImg( 0, 0, 0);
    ws2811.sendLedData();
    delay(20);    
  }
  
  // fps computation
  ++nCpt;
  ++nFpsCpt;
  const int nNbrFrameToCompute = 100; // 10000*2, c'est bien pour du 5000fps :)
  if( nFpsCpt == nNbrFrameToCompute )
  {
    unsigned long nNow = micros();
    unsigned long nDuration = nNow - timeFpsBegin;
    
    Serial.print( "frame: " );
    Serial.print( nDuration/nNbrFrameToCompute );
    Serial.print( "us, fps: " );
    Serial.println( 1000000.*nNbrFrameToCompute/nDuration );
    timeFpsBegin = nNow;
    nFpsCpt = 0;
    
    // a simple analog read is running at 5413fps (184us per frame)
  }
}

/**
 * HVS to RGB conversion (simplified to the range 0-255)
 **/
 
 void getHue( int h, CRGB * pRes )
 {
     //this is the algorithm to convert from RGB to HSV
  double r=0; 
  double g=0; 
  double b=0;

//  double hf=h/42.5; // Not /60 as range is _not_ 0-360

  int i=(int)floor(h/42.5);
  double f = h/42.5 - i;
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

  pRes->r = constrain((int)255*r,0,255);
  pRes->g = constrain((int)255*g,0,255);
  pRes->b = constrain((int)255*b,0,255);
 }

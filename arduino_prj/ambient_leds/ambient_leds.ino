#include <EEPROM.h>

/*
 * La table des Aromes des Caves du Louvre
 * 
 * Version number: cf the message in the print of the setup function
 * Author: Alexandre Mazel
 * copyright (c) A.Mazel 2015
 
 * compiled with Arduino 1.0.6
 */

#include "Ai_WS2811.h"

const int nLedPin = 53; // one led per reader
const int nNbrLeds = 5; // Enter here your real number of leds (90 in the kitchen 60 on my remaining leds)
Ai_WS2811 ws2811;
struct CRGB * apLeds[1] = {NULL};

int nAnimFrame=0;
int nLightTimeOut=0;
int nStage = 0; // 0: wait, 1: on
int nIntensity=0;


////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
void setup()
{
  int i;
  Serial.begin(115200);
  
  pinMode( nLedPin, OUTPUT );

  ws2811.init(nLedPin,nNbrLeds);
  apLeds[0] = (struct CRGB*)ws2811.getRGBData();

  // turn them all low (not working)
  ws2811.setDim( 16 );
  
  Serial.println( "\nArduino started: Ambient leds v0.6\n" );
  
  Serial.print( "nLedPin: " );
  Serial.println( nLedPin, DEC );

  Serial.print( "nNbrLeds: " );
  Serial.println( nNbrLeds, DEC );

/*
  Serial.println("two led on for 2 sec");
  ws2811.setOneBrightOtherLow( nNbrLeds, 2, 2, 10, 64, 64, 0, 0, 0 ); // allume en violet la led 2 et 3
  ws2811.sendLedData();
  delay(4000);
*/

}


void justLightOn( void )
{
  if( nAnimFrame <= 196 )
  {
    ws2811.setColor( nAnimFrame, nAnimFrame, nAnimFrame );
    ++nAnimFrame;    
  }
}

void christmas();

void vuMeterOn( void )
{
  ws2811.setDim( 2 );
  if( nAnimFrame <= 10000/80 )
  {
    ws2811.setVumeter( nAnimFrame*80 );
    ++nAnimFrame;    
  }
  else if( nAnimFrame < 10000/80+4 )
  {
    ws2811.setDim( 1 );    
    ws2811.setColor( 200, 200, 200 );
    for( int j = 0; j < 5; ++j )
    {
      // 5 first one full bright for cuisiniere
      apLeds[0][j].g = 255;
      apLeds[0][j].r = 255;
      apLeds[0][j].b = 255;      
    }
    ws2811.sendLedData();
    ++nAnimFrame;
    
  }
  else
  {
    // extinction automatique
    int i;
    for( i = 0; i < 60*60; ++i ) // 1h00min
    {
      delay(1000);
    }
    for( i=200;i>=0;--i)
     {
       ws2811.setColor( i, i, i );
       delay(20);
     }
     // juste une verte:
     ws2811.setOnlyOne( 45, 0, 255, 0 );
     
     // 4 leds blanche
    for( int i=0; i < 5; ++i )
    {
      apLeds[0][i/5*nNbrLeds].g = 200;
      apLeds[0][i/5*nNbrLeds].r = 200;
      apLeds[0][i/5*nNbrLeds].b = 150;        
    }
    ws2811.sendLedData();
     if( 1 )
     {
       // version boucle infini
       for(;;)
       {
         delay(10000); // end of program
       }
     }
     else
     {
       // version de Noel
       christmas();
     }
  }
  delay(20);
}
int nLifeMax = 2000; // 2000
int nLife = nLifeMax;
int nColor=1; // red/green/blue/violet/...
int nIdx = 0;
int nDir = 1;
int nMotif = 2;
void party()
{
  if( nLife > 0 )
  {
    if( nMotif == 0 )
    {
      ws2811.setOneBrightOtherLow( nNbrLeds, 0, nIdx, 255, 0, 0, 10, 10, 10 );
      ws2811.sendLedData();
      //delay(10);
    }
    else if( nMotif == 1 )
    {
      ws2811.setOnlyOne( random(10000), 255, 50, 50 );
      //delay(80);
    }
    else if( nMotif == 2 )
    {
      ws2811.setOnlyOne( random(10000), 255, 50, 50 );
      ws2811.sendLedData();
      for( int i=0; i < 20; ++i )
      {
        uint8_t grey = random(256);
        int pix = random(nNbrLeds);
        apLeds[0][pix].g = grey;
        apLeds[0][pix].r = grey;
        apLeds[0][pix].b = grey;
      }
      ws2811.sendLedData();
      delay(4);      
    }
    else if( nMotif == 3 )
    {
      ws2811.setOnlyOne( random(10000), 255, 50, 50 );
      ws2811.sendLedData();
      for( int i=0; i < 20; ++i )
      {
        apLeds[0][random(nNbrLeds)].g = random(256);
        apLeds[0][random(nNbrLeds)].r = random(256);
        apLeds[0][random(nNbrLeds)].b = random(256);        
      }
      ws2811.sendLedData();
      delay(4);
    }    
    nIdx += nDir;
    if( nIdx >= nNbrLeds || nIdx < 0 )
    {
      nDir *= -1;
      nIdx += nDir;
      nIdx += nDir;
    }
    --nLife;
  }
  else
  {
    nLife = nLifeMax;
    nMotif +=1;
    if( nMotif > 3 )
    {
      nMotif = 0;
    }
  }
 
}

void christmas()
{
  const int nDim = 16;
   while( 1 )
   {
     int nSwitch = random( 2 ); // 3 => 2 coup sur 3 la guirlande cool
     //nSwitch = 0;
     Serial.print("DBG: christmas: nSwitch: ");
     Serial.println(nSwitch);
     if( nSwitch != 0 )
     {
       for( int j = 0; j < 10; ++j )
       {
         int nPause = 500;
         ws2811.setColor( 255/nDim, 0, 0 );
         delay(nPause);
         ws2811.setColor( 0, 255/nDim, 0 );
         delay(nPause); 
         ws2811.setColor( 0, 0, 255/nDim );
         delay(nPause);
         ws2811.setColor( 128/nDim, 0, 128/nDim );
         delay(nPause);
         ws2811.setColor( 128/nDim, 128/nDim, 0 );
         delay(nPause);       
         ws2811.setColor( 0, 128/nDim, 128/nDim );
         delay(nPause);              
       }
     }
     else
     {
       for( int j = 0; j < 300; ++j )
       {         
          ws2811.setOnlyOne( random(10000), 255/nDim, 50/nDim, 50/nDim );
          //ws2811.sendLedData();
          for( int i=0; i < 30; ++i )
          {
            uint8_t grey = random(256)/nDim;
            int pix = random(nNbrLeds);
            apLeds[0][pix].g = grey;
            apLeds[0][pix].r = grey;
            apLeds[0][pix].b = grey;
          }
          ws2811.sendLedData();
          delay(40);       
       }
     }
   }
}


void loop()
{
 // reactUS();
 // justLightOn();
  //vuMeterOn();
 // party();
 christmas();

  //ws2811.setColor(0,0,0);
 
  delay(1);
}

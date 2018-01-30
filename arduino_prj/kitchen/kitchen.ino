#include <EEPROM.h>

/*
 * La table des Aromes des Caves du Louvre
 * 
 * Version number: cf the message in the print of the setup function
 * Author: Alexandre Mazel
 * copyright (c) A.Mazel 2015
 
 * compiled with Arduino 1.0.6
 */

#include "NewPing.h"
#include "Ai_WS2811.h"

const int nFirstLedPin = 53; // one led per reader
const int nNbrLeds = 90; // 90
Ai_WS2811 ws2811;
struct CRGB * apLeds[1] = {NULL};

const int nPinUsTrig = 12;
const int nPinUsEcho = 11;

////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////
void setup()
{
  int i;
  Serial.begin(9600);
  pinMode( nFirstLedPin, OUTPUT );

  ws2811.init(nFirstLedPin,nNbrLeds);
  apLeds[0] = (struct CRGB*)ws2811.getRGBData();
  ws2811.setDim( 1 );

  
  Serial.println( "\nArduino started: Kitchen v0.6\n" );
  
  Serial.print( "nFirstLedPin: " );
  Serial.println( nFirstLedPin, DEC );
  
  pinMode(nPinUsTrig, OUTPUT);
  digitalWrite(nPinUsTrig, LOW); // La broche TRIGGER doit être à LOW au repos
  pinMode(nPinUsEcho, INPUT);  
}

const unsigned long MEASURE_TIMEOUT = 25000UL; // Constantes pour le timeout: 25ms = ~8m à 340m/s
const float SOUND_SPEED = 340.0 / 1000; // Vitesse du son dans l'air en mm/us

#define MAX_DISTANCE 300
NewPing sonar(nPinUsTrig, nPinUsEcho, MAX_DISTANCE);

// return the distance in mm
int nPrev=0;
int readDistance()
{
  
    //delay(150);
    
    int uS = sonar.ping_cm(500)*10;
  if( uS==0 || 0 )
  {
    //Serial.println("MAX: resetting sensor");
    pinMode(nPinUsEcho, OUTPUT);
    //delay(150);
    digitalWrite(nPinUsEcho, LOW);
    delayMicroseconds(200);
    pinMode(nPinUsEcho, INPUT);
    //delay(150);
  }    
    uS = (nPrev*7+uS*1)/8;
    nPrev = uS;
  
    Serial.println( uS );  // problem du capteur: http://therandomlab.blogspot.fr/2015/05/repair-and-solve-faulty-hc-sr04.html
    return uS;
  
  
  // 1. Lance une mesure de distance en envoyant une impulsion HIGH de 10µs sur la broche TRIGGER
  digitalWrite(nPinUsTrig, LOW);
  delayMicroseconds(2);
  
  digitalWrite(nPinUsTrig, HIGH);
  delayMicroseconds(10);
  digitalWrite(nPinUsTrig, LOW);
  
  // Mesure le temps entre l'envoi de l'impulsion ultrasonique et son écho (si il existe)
  //long measure = pulseIn(nPinUsEcho, HIGH, MEASURE_TIMEOUT); // if 0 => timeout
  long measure = pulseIn(nPinUsEcho, HIGH );
  Serial.println( measure );
  if( measure==0 && 0 )
  {
    Serial.println("MAX: resetting sensor");
    pinMode(nPinUsEcho, OUTPUT);
    delay(150);
    digitalWrite(nPinUsEcho, LOW);
    delay(150);
    pinMode(nPinUsEcho, INPUT);
    delay(150);
  }
   
  // 3. Calcul la distance à partir du temps mesuré
  float distance_mm = measure / 2.0 * SOUND_SPEED;
   
  // Affiche les résultats en mm, cm et m
  Serial.print(F("Distance: "));
  Serial.print(distance_mm);
  Serial.print(F("mm ("));
  Serial.print(distance_mm / 10.0, 2);
  Serial.print(F("cm, "));
  Serial.print(distance_mm / 1000.0, 2);
  Serial.println(F("m)"));
  delay(500);
}

int nAnimFrame=0;
int nLightTimeOut=0;
int nStage = 0; // 0: wait, 1: on
int nIntensity=0;
int nCptNoMeasure = 0;

void reactUS( void )
{
    ++nCptNoMeasure;
  if( nCptNoMeasure > 10 )
  {
      //int nDist = readDistance();
      //if( nDist < 1800 && nDist != 0 )
      if(1)
      {
       if( nStage == 0 )
       {
         Serial.println("light on");
        nStage=1;
       }
       nLightTimeOut = 100*5; // 1 min
      }
      
      nCptNoMeasure = 0;
  }

  if( nStage == 1 )
  {
    --nLightTimeOut;
    if( nLightTimeOut == 0 )
    {
     Serial.println("light off");      
      nStage = 0;
    }      
  }
  
  if( nStage == 0 && nIntensity > 0 )
  {
    --nIntensity;
    ws2811.setColor( nIntensity, nIntensity, nIntensity );    
  }
  if( nStage == 1 && nIntensity < 255 )
  {
    ++nIntensity;
    ws2811.setColor( nIntensity, nIntensity, nIntensity );
  } 
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
    for( i = 0; i < 30*60; ++i ) // 30min
    {
      delay(1000);
    }
    for( i=200;i>=0;--i)
     {
       ws2811.setColor( i, i, i );
       delay(20);
     }
     ws2811.setOnlyOne( 45, 0, 255, 0 );
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
   while( 1 )
   {
     int nSwitch = random( 2 ); // 3 => 2 coup sur 3 la guirlande cool
     //nSwitch = 0;
     if( nSwitch != 0 )
     {
       for( int j = 0; j < 10; ++j )
       {
         int nPause = 500;
         ws2811.setColor( 255, 0, 0 );
         delay(nPause);
         ws2811.setColor( 0, 255, 0 );
         delay(nPause); 
         ws2811.setColor( 0, 0, 255 );
         delay(nPause);
         ws2811.setColor( 128, 0, 128 );
         delay(nPause);
         ws2811.setColor( 128, 128, 0 );
         delay(nPause);       
         ws2811.setColor( 0, 128, 128 );
         delay(nPause);              
       }
     }
     else
     {
       for( int j = 0; j < 300; ++j )
       {         
          ws2811.setOnlyOne( random(10000), 255, 50, 50 );
          //ws2811.sendLedData();
          for( int i=0; i < 30; ++i )
          {
            uint8_t grey = random(256);
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
  vuMeterOn();
 //party();
 
  delay(1);
}

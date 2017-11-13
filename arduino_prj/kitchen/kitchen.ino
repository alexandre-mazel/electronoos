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
const int nNbrLeds = 90;
Ai_WS2811 ws2811;
struct CRGB * apLeds[1] = {NULL};

const int nPinUsTrig = 8;
const int nPinUsEcho = 9;

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
int readDistance()
{
  
    delay(150);
    int uS = sonar.ping();
    Serial.println( uS );  
  if( uS==0 && 0 )
  {
    Serial.println("MAX: resetting sensor");
    pinMode(nPinUsEcho, OUTPUT);
    delay(150);
    digitalWrite(nPinUsEcho, LOW);
    delay(150);
    pinMode(nPinUsEcho, INPUT);
    delay(150);
  }    
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

int nFrame = 0;
void loop()
{
  int nCoef = 2;
  if( nFrame <= 255*nCoef )
  {
    ws2811.setColor( nFrame/nCoef, 0, 0 );
    ++nFrame;
  }
  readDistance();
  delay(1);
}

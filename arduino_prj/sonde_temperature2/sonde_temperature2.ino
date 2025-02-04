#include <arduino.h>
#include "ds18b20_onewire.hpp"

void setup()
{
  Serial.begin(115200);
  OneWire_setup();
}

void loop()
{
  float t1, t2, t3, t4, t5;
  t1 = t2 = t3 = t4 = t5 = -421.0f;
  // on pourrait en mettre 5, mais je veux tester aussi si on en met que 4, pour la gestion du NULL
  int nReaded = OneWire_getAllTemperature( &t1, &t2, &t3, &t4 );
  Serial.print( "OneWire_temp: nReaded: " ); Serial.print( nReaded ); Serial.print( ", t1: " ); Serial.print( t1, 1 ); Serial.print( ", t2: " ); Serial.print( t2, 1 );Serial.print( ", t3: " ); Serial.print( t3, 1 );Serial.print( ", t4: " ); Serial.print( t4, 1 ); Serial.print( ", t5: " ); Serial.println( t5, 1 );
  // 2025-02-04: ca a fonctionne nickel: teste avec 3 capteurs en D12 (PWM) sur Arduino Mega2560: ok (la lecture prend a peu pres 1 sec)
  // Les 3 capteurs valaient 17.4, 17.6 et 17.85
  delay(1000);
}
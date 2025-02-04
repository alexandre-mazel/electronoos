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
  // on pourrait en mettre 5, mais je veux tester aussi si on en met que 4
  int nReaded = OneWire_getAllTemperature( &t1, &t2, &t3, &t4 );
  Serial.print( "OneWire_temp: nReaded: " ); Serial.print( nReaded ); Serial.print( ", t1: " ); Serial.print( t1, 1 ); Serial.print( ", t2: " ); Serial.print( t2, 1 );Serial.print( ", t3: " ); Serial.print( t3, 1 );Serial.print( ", t4: " ); Serial.print( t4, 1 ); Serial.print( ", t5: " ); Serial.println( t5, 1 );

  delay(1000);
}
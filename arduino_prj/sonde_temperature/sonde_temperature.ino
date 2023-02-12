#include "OneWire.h"
#include "DallasTemperature.h"
 
OneWire oneWire(A1);
DallasTemperature ds(&oneWire);

void setup() {
  Serial.begin(9600);  // definition de l'ouverture du port serie
  ds.begin();          // sonde activee
}

void loop() {
  if( 0 )
  {
    ds.requestTemperatures();
    int t = ds.getTempCByIndex(0);
    Serial.print(t);
    Serial.println( "C" );
   delay(1000);
  }
  else
  {
    int v;
    v =  analogRead(A1);
    Serial.println( v );
    delay(10);
  }

}
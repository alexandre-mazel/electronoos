#include <arduino.h>

#define PIN_PHOTORES  A15

void setup()
{
  Serial.begin(57600);
  pinMode( PIN_PHOTORES, INPUT );
}

void loop()
{
   int valeurphotores = analogRead(PIN_PHOTORES);

   Serial.print("res: ");
   Serial.print(valeurphotores);

   Serial.print(", ");

   if( valeurphotores > 300 )
   {
    Serial.print("light!");
   }
   else
   {
    Serial.print("shadow.");
   }
   Serial.println("");

   delay(500);
}
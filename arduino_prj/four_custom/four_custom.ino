
const int analogPin = A3;
const int chauffePin1 = 30;
const int chauffePin2 = 31;

const int rThermalResistanceReference = 678.0; // avec 678, on a une precision de 2.5 ohm soit 0.15degrees
// je suis monté a genre ~100 et j'ai une resistance de 900ohm soit 56.3, ma formule est fausse (ou alors du moins il y a une constante)

// a 88.6 mesuré, je lis: 690.04 resistance

#define USE_TEMP_REF_DALLAS

#ifdef USE_TEMP_REF_DALLAS
#define DS18B20MODEL 0x28
#include "OneWire.h"
#include "DallasTemperature.h"

const int tempDallasPin = 7; // D7

OneWire ds(tempDallasPin);
DallasTemperature sensors(&ds);
#endif // USE_TEMP_REF_DALLAS



void setup() 
{
  Serial.begin(57600);           //  setup serial

#ifdef USE_TEMP_REF_DALLAS
  Serial.println("INF: using Dallas");
  pinMode(tempDallasPin,INPUT);
  sensors.begin();          // sonde activee
#endif // USE_TEMP_REF_DALLAS

  pinMode(chauffePin1, OUTPUT);
  pinMode(chauffePin2, OUTPUT);
  digitalWrite(chauffePin1, HIGH);
  digitalWrite(chauffePin2, HIGH);

  Serial.println("Starting...");
  delay(1000);

}

float inputToResistance( int nAnalogValue, const float rKnownResistance )
{
  const float rVin = 5.0f;
  float rVoltageMeasured = nAnalogValue*(rVin /1023.0);
  float resistance = rKnownResistance * ( 1/(rVin/rVoltageMeasured-1) );
  Serial.print("nAnalogValue: "); Serial.print(nAnalogValue); Serial.print(", rVin: "); Serial.print(rVin,2); Serial.print(", rVoltageMeasured: "); Serial.print(rVoltageMeasured,2); Serial.print(", resistance: "); Serial.println(resistance,2);
  return resistance;
}

void loop()
{
  int val = analogRead(analogPin);
  float resistance = inputToResistance(val, rThermalResistanceReference);
  float temperature = resistance / 16.;

#ifdef USE_TEMP_REF_DALLAS
  sensors.requestTemperatures();
  float tRef = sensors.getTempCByIndex(0);
#endif

  Serial.print("resistance: ");
  Serial.print(resistance,2);
  Serial.print(", temperature: ");
  Serial.print(temperature,2);
#ifdef USE_TEMP_REF_DALLAS
  Serial.print(", temp_ref: ");
  Serial.print(tRef,2);
#endif
  Serial.println();

  float target = 100;
  if(temperature < 10 ||temperature > 300 )
  {
    Serial.println("EMERGENCY. Turning off!");
    digitalWrite(chauffePin1, HIGH);
    digitalWrite(chauffePin1, HIGH);
    delay(5000);
    return;
  }
  if( temperature > target+5 )
  {
    digitalWrite(chauffePin2, HIGH);
    digitalWrite(chauffePin1, HIGH);
    Serial.println( "Chauffe STOP");

  }
  else if( temperature < target -5 )
  {
    digitalWrite(chauffePin1, LOW);
    digitalWrite(chauffePin2, LOW);
    Serial.println( "Chauffe START");
  }
  delay(500);
}

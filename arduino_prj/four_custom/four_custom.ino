
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

#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 20, 4);

bool i2CAddrTest(uint8_t addr) {
  Wire.begin();
  Wire.beginTransmission(addr);
  if (Wire.endTransmission() == 0) {
    return true;
  }
  return false;
}


char tabAnim[] = "-\\|/"; // antislash is bugged

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

  if (!i2CAddrTest(0x27)) 
  {
    Serial.println("Alternate init on 0x3F");
    lcd = LiquidCrystal_I2C(0x3F, 20, 4);
  }
  lcd.init();                // initialize the lcd
  lcd.backlight();           // Turn on backlight // sans eclairage on voit rien...

  lcd.print("Four AlexBraun v2.0");

  lcd.setCursor(0, 2);
  lcd.print("Four ready");

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

long int nNumFrame = 0;

void loop()
{
  float target = 200;

  int val = analogRead(analogPin);
  float resistance = inputToResistance(val, rThermalResistanceReference);
  float temperature = 16.75+(resistance - 544)*0.4377; // cf hack four spreadsheet

#ifdef USE_TEMP_REF_DALLAS
  sensors.requestTemperatures();
  float tRef = sensors.getTempCByIndex(0);
#endif

  Serial.print("resistance: ");
  Serial.print(resistance,2);
  Serial.print(", temperature: ");
  Serial.print(temperature,2);
  Serial.print(", target: ");
  Serial.print(target,2);
#ifdef USE_TEMP_REF_DALLAS
  Serial.print(", temp_ref: ");
  Serial.print(tRef,2);
#endif
  Serial.println();

  bool bEnChauffe = 0;

  if(temperature < 10 ||temperature > 280 )
  {
    Serial.println("EMERGENCY. Turning off!");
    digitalWrite(chauffePin1, HIGH);
    digitalWrite(chauffePin1, HIGH);
    lcd.setCursor(0, 2);
    lcd.print("Probleme capteur !");
    delay(5000);
    return;
  }
  const int nHisteresis = 2;
  if( temperature > target + nHisteresis )
  {
    digitalWrite(chauffePin2, HIGH);
    digitalWrite(chauffePin1, HIGH);
    Serial.println( "Chauffe STOP");

  }
  else if( temperature < target - nHisteresis )
  {
    digitalWrite(chauffePin1, LOW);
    digitalWrite(chauffePin2, LOW);
    Serial.println( "Chauffe START");
    bEnChauffe = 1;
  }
  lcd.setCursor(0, 1);
  lcd.print("Target: ");
  lcd.print(target);

  lcd.setCursor(0, 2);
  lcd.print("Actual: ");
  lcd.print(temperature);
  lcd.print(" (");
  lcd.print(int(tRef));
  lcd.print(")");

  lcd.setCursor(0, 3);
  lcd.print(tabAnim[nNumFrame%4]);
  
  if(bEnChauffe)
  {
    lcd.print(" En chauffe !!!");
  }
  else
  {
    lcd.print(" ------------");
  }

  nNumFrame += 1;

  delay(1000);
  
}

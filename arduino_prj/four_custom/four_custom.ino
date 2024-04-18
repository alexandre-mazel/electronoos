const int analogPin = A3;

const int rThermalResistanceReference = 678.0;

void setup() 
{
  Serial.begin(57600);           //  setup serial
}

float inputToResistance( int nAnalogValue, const float rKnownResistance )
{
  const float rVin = 5.0f;
  float rVoltageMeasured = nAnalogValue*(rVin /1023.0);
  float resistance = rKnownResistance * ( 1/(rVin/rVoltageMeasured-1) );
  Serial.print("rVin: "); Serial.print(rVin,2); Serial.print(", rVoltageMeasured: "); Serial.print(rVoltageMeasured,2); Serial.print(", resistance: "); Serial.println(resistance,2);
  return resistance;
}

void loop()
{
  int val = analogRead(analogPin);
  float resistance = inputToResistance(val, rThermalResistanceReference);
  Serial.print("resistance: ");
  Serial.println(resistance,2);
  delay(500);
}

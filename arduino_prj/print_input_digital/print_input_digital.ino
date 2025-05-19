
#define FIRST_PIN 20
#define LAST_PIN 50

void setup()
{
  Serial.begin(57600);


  for( int i = FIRST_PIN; i < LAST_PIN; ++i )
  {
    pinMode( i, INPUT );
  }
}

void loop()
{
  for( int i = FIRST_PIN; i < LAST_PIN; ++i )
  {
    int val = digitalRead(i) == HIGH;
    Serial.print(i);
    Serial.print(": ");
    Serial.print(val);
    Serial.print(", ");
  }
  Serial.println("");

  delay(500);
}
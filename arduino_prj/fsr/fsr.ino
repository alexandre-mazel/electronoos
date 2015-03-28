#define SENSOR_PIN 0


//some initial values
void setup()
{
    Serial.begin(9600);
}

void loop()
{
    int nVal = analogRead(  SENSOR_PIN ); // nLight is big when darker
    Serial.println( nVal );
    delay(100);
}


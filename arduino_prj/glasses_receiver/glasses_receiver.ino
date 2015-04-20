#define LED_PIN 13

void setup()
{
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  for( int i = 0; i < 10; ++i )
  {
    digitalWrite(LED_PIN, HIGH);
    delay( 100 );
    digitalWrite(LED_PIN, LOW);    
    delay( 200 );      
  }
}

void loop()
{
    while(Serial.available())
    {
      unsigned char buf = Serial.read();
      if( buf > 128 )
      {
        digitalWrite(LED_PIN, HIGH);
      }
      else
      {
        digitalWrite(LED_PIN, LOW);
      }
    }
}

#define LED_PIN 13

void debug_with_led( unsigned char B )
{
  // Print a long then one impulsion per byte
  digitalWrite(LED_PIN, HIGH);   
  delay( 1000 );
  digitalWrite(LED_PIN, LOW);
  delay( 100 );          
  for( int i = 0; i < 8; ++i )
  {
    if( (1<<i) & B )
    {
      digitalWrite(LED_PIN, HIGH);
    }
    else
    {
      digitalWrite(LED_PIN, LOW);
    }
    delay( 400 );
    digitalWrite(LED_PIN, LOW);
    delay( 100 );      
  }
}

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
  
  // debug_with_led( 0 );
  // debug_with_led( 0xFF );  
}

//unsigned char nLedValue = 0;
void loop()
{
    while(Serial.available())
    {
      unsigned char buf = Serial.read();
      if( 0 ) debug_with_led( buf );
      
      if( 1 )
      {
        if( buf >= 50 )
        {
          digitalWrite(LED_PIN, HIGH);
          // delay(1000);
        }
        else
        {
          digitalWrite(LED_PIN, LOW);
        }
      }
    }
}

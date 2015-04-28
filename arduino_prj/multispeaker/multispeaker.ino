int ledPin = 13;
int speakerPin = 3; // Can be either 3 or 11, two PWM outputs connected to Timer 2

void setup()
{
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, HIGH);
}

void playTone(int tone, int duration)
{
  for (long i = 0; i < duration * 1000L; i += tone * 2) {
    digitalWrite(speakerPin, HIGH);
    delayMicroseconds(tone*1);
    digitalWrite(speakerPin, LOW);
    delayMicroseconds(tone*1);
  }
}

void loop()
{
  digitalWrite(ledPin, LOW);  
  playTone( 1000, 1000 );
  digitalWrite(ledPin, HIGH);  
  playTone( 1900, 1000 );
  
}


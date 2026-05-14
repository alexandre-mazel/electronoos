#define VANNE_PIN 32+4

void setup() 
{
  pinMode(VANNE_PIN, OUTPUT);
}

void loop()
{
  int timeHache=500;
  for(int i = 0; i < 10; ++i)
  {
      digitalWrite(VANNE_PIN, LOW);
      delay(timeHache);

      digitalWrite(VANNE_PIN, HIGH);
      delay(timeHache);
  }

  digitalWrite(VANNE_PIN, HIGH);
  delay(5*1000);
}
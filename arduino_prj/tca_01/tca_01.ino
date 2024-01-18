#include <Encoder.h> // by Paul Stoffregen

Encoder enc1(18,19);

void setup() 
{
  Serial.begin(9600);       // use the serial port
}

void loop() 
{
  int val = enc1.read();
  Serial.println(val);
}
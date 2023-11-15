#include "HX711.h" // install in the library manager the HX711 by Rob Tillart (for cell amplifier)
#include <LiquidCrystal.h>


// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

//#define CLK A0
//#define DOUT A1

HX711 scale;
float calibration_factor = 1.;

/*
long read_average(byte times = 10); // Average 'times' raw readings
double get_value(byte times = 1); // return read_average(times) - OFFSET
float get_units(byte times = 1); // return get_value(times) / SCALE;
void tare(byte times = 10); // OFFSET = read_average(times);

So, get_units() returns (read_average(1) - OFFSET) / SCALE;
*/


void setup() {
  
  Serial.begin(9600);
  //pinMode(resetPin, INPUT);


  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  while(!scale.is_ready())
  {
    Serial.println("INF: Waiting for HX711...");
    delay(500);
  }
  scale.set_scale(calibration_factor);
  scale.tare();                           // reset weight on scale to 0 grams
  delay(500);
  long zero_factor = scale.read_average();
  Serial.print("Zero factor: ");
  Serial.println(zero_factor);
  delay(500);
}

void loop() {
  
  
  if (!scale.is_ready()) 
  {
    Serial.println("HX711 not found.");
  }
  else
  {
    Serial.print("calibration_factor: ");
    Serial.println(calibration_factor);
    scale.set_scale(calibration_factor);   
    if(0)
    { 
      // tare and measure in same loop
      Serial.println("Tare... remove any weights from the scale.");
      delay(5000);
      scale.tare();
      Serial.println("Tare done...");
      Serial.print("Place a known weight on the scale...");
      delay(5000);
    }
    float reading = scale.get_units(10);
    Serial.print("Result: ");
    Serial.println(reading);
    reading = scale.read_average();
    Serial.print("Result avg: ");
    Serial.println(reading);
    if(1)
    {
      Serial.println("press key to change calibration factor");
      if(Serial.available())
      {
        char input = Serial.read();
        if(input == 'a'){ calibration_factor += 100; }
        else if(input == 'z'){  calibration_factor -= 100; }
        else if(input == 's'){  calibration_factor += 10; }
        else if(input == 'x'){  calibration_factor -= 10; }
        else if(input == 'd'){  calibration_factor += 1; }
        else if(input == 'c'){  calibration_factor -= 1; }
      }
    }
  }
  delay(1000);
}
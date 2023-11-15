#include "HX711.h" // install in the library manager the HX711 by Rob Tillart (for cell amplifier)
#include <LiquidCrystal.h>


// HX711 circuit wiring
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

//#define CLK A0
//#define DOUT A1

HX711 scale;

void setup() {
  
  Serial.begin(9600);
  //pinMode(resetPin, INPUT);

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  //scale.set_scale(calibration_factor);
  scale.tare();                           // reset weight on scale to 0 grams

}

void loop() {
  float weight = scale.get_units();
  Serial.print("Weight: ");
  Serial.println(weight);

  //if(digitalRead(resetPin) == 0){
//    scale.tare();     // reset weight on scale to 0 grams
  //}
  scale.power_down();             // put the ADC in sleep mode
  delay(10);
  
  scale.power_up(); 
}
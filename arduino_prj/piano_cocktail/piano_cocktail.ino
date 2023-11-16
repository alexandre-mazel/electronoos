#include "HX711.h" // install in the library manager the HX711 by Rob Tillart (for cell amplifier)
#include <LiquidCrystal.h>


// HX711 circuit wiring

// digital or analogic, quand ca fonctionne ca fonctionne...
#if 0
// digital ?
const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;
#else

// or analogic ?
//#define CLK A0
//#define DOUT A1
const int LOADCELL_DOUT_PIN = A1;
const int LOADCELL_SCK_PIN = A0;

#endif

HX711 scale;
// si plus petit, ca surcote un peu (les poids affiché semblent etre plus lourd que la réalité)

// reglage pour la barre de 10kg:

//float calibration_factor = 205; // when set to 1, it's = read/known value // poid de 1kg: 206.9, poid de 20g: 193.68
// avec 200:
// poids de gym, l'une a 1041 et l'autre a 1036
// poids de 20g+10g, entre 29.10 et 29.38

// reglage pour barre de 3kg:

float calibration_factor = 733; // 30g => 22000: 733 [une bouteille vide (celle de blanc orschwiller) peserait 448g]


float old_calibration_factor = calibration_factor;


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
  Serial.print("calibration_factor: ");
  Serial.println(calibration_factor);
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
    if(old_calibration_factor != calibration_factor)
    {
      old_calibration_factor = calibration_factor;
      Serial.print("new calibration_factor: ");
      Serial.println(calibration_factor);
      scale.set_scale(calibration_factor);
      Serial.println("re-taring...");
      scale.tare(); 
    }
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
    float reading = scale.get_units(20);
    Serial.print("Result: ");
    Serial.print(reading);
    Serial.print(" => ");
    Serial.print(int(round(reading)));
    Serial.println(" g");
    long raw = scale.read_average();
    Serial.print("Result raw avg: ");
    Serial.println(raw);
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
        else if(input == 'r'){  calibration_factor = 1; }
        else if(input == 't'){  Serial.println("re-taring..."); scale.tare();}
      }
    }
  }
  delay(1000);
}
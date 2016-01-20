// Pin à connecter à la feuille de papier
int capSensePin = 3;
// Seuil de détection du capteur, à régler par essais
int touchedCutoff = 60;

void setup(){
  Serial.begin(9600);
  // Mise en place de la LED
  pinMode(LEDPin, OUTPUT);
  digitalWrite(LEDPin, LOW);
  Serial.println("Capacitive Sensor Test");  
}


void buzz(int targetPin, long frequency, long length) {
  long delayValue = 1000000/frequency/2;
  long numCycles = frequency * length/ 1000;
  for (long i=0; i < numCycles; i++)
  {
    digitalWrite(targetPin,HIGH);
    delayMicroseconds(delayValue);
    digitalWrite(targetPin,LOW);
    delayMicroseconds(delayValue);
  }
}


int nCpt = 0;
void loop(){
  
  // Si le capteur atteint un certain seuil de tension, la led s'allume
  
/*  
  if (readCapacitivePin(capSensePin) > touchedCutoff) {
    digitalWrite(LEDPin, HIGH);
    // utilisation
    buzz(4, 2500, 1000); // buzz sur pin 4 à 2500Hz
  }
  else {
    digitalWrite(LEDPin, LOW);
  }
*/  
  // Affiche toutes les 500 millisecondes la valeur du capteur
  //if ( (millis() % 500) == 0)
  if( (nCpt % 100) == 0 )
  {
    Serial.print("Capacitive Sensor reads: ");
    Serial.println(readCapacitivePin(capSensePin));
  }
  ++nCpt;
  delay(5);
}


// read a capacitive value
//  pinToMeasure: the pin to which is attached the capacitive
//  Return: a number, increased when finger approach
uint8_t readCapacitivePin(int pinToMeasure)
{
  // This is how you declare a variable which
  //  will hold the PORT, PIN, and DDR registers
  //  on an AVR
  volatile uint8_t* port;
  volatile uint8_t* ddr;
  volatile uint8_t* pin;
  // Here we translate the input pin number from
  //  Arduino pin number to the AVR PORT, PIN, DDR,
  //  and which bit of those registers we care about.
  byte bitmask;
  if ((pinToMeasure >= 0) && (pinToMeasure <= 7)){
    port = &PORTE; // Alma: was PORTD for Uno (here for ATMEGA)
    ddr = &DDRE; // Alma: was DDRE for Uno (here for ATMEGA)
    bitmask = 1 << (pinToMeasure+2); // Alma: was +0 (here for ATMEGA)
    pin = &PINE; // Alma: was &PIND (here for ATMEGA)
  }
  if ((pinToMeasure > 7) && (pinToMeasure <= 13)){
    port = &PORTB;
    ddr = &DDRB;
    bitmask = 1 << (pinToMeasure - 8);
    pin = &PINB;
  }
  if ((pinToMeasure > 13) && (pinToMeasure <= 19)){
    port = &PORTC;
    ddr = &DDRC;
    bitmask = 1 << (pinToMeasure - 13);
    pin = &PINC;
  }
  // Discharge the pin first by setting it low and output
  *port &= ~(bitmask);
  *ddr  |= bitmask;
  delay(1);
  // Make the pin an input WITHOUT the internal pull-up on
  *ddr &= ~(bitmask);
  // Now see how long the pin to get pulled up
  int cycles = 16000;
  for(int i = 0; i < cycles; i++){
    if (*pin & bitmask){
      cycles = i;
      break;
    }
  }
  // Discharge the pin again by setting it low and output
  //  It's important to leave the pins low if you want to 
  //  be able to touch more than 1 sensor at a time - if
  //  the sensor is left pulled high, when you touch
  //  two sensors, your body will transfer the charge between
  //  sensors.
  *port &= ~(bitmask);
  *ddr  |= bitmask;
  
  return cycles;
}

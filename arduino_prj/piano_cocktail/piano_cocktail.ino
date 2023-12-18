#include "HX711.h" // install in the library manager the HX711 by Rob Tillart (for cell amplifier)
#include <LiquidCrystal.h>


// HX711 circuit wiring

// digital or analogic, quand tout est bien branché ca fonctionne avec les 2 types...
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

float calibration_factor = 733; // 30g => 22000: 733 [une bouteille vide (celle de blanc orschwiller) peserait 448g; le plateau en fer 352g]


float old_calibration_factor = calibration_factor;


/*
long read_average(byte times = 10); // Average 'times' raw readings
double get_value(byte times = 1); // return read_average(times) - OFFSET
float get_units(byte times = 1); // return get_value(times) / SCALE;
void tare(byte times = 10); // OFFSET = read_average(times);

So, get_units() returns (read_average(1) - OFFSET) / SCALE;
*/

const int VANNE_1_PIN = 7;

#include <LiquidCrystal_I2C.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal_I2C lcd(0x3F, 16, 2);

void setup() {
  
  Serial.begin(9600);
  //pinMode(resetPin, INPUT);

  pinMode(VANNE_1_PIN, OUTPUT);
  digitalWrite(VANNE_1_PIN, HIGH); // high don't send voltage !?!
  
  lcd.init();                // initialize the lcd
  lcd.backlight();           // Turn on backlight // sans eclairage on voit rien...
  lcd.setCursor(0, 0);
  lcd.print("taring...");

  
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
  lcd.clear();
}

float last_measured = 0;


// ask to verse x grammes
float target_verse = -1001; // negative when no current
void verse_quantite(float rGrammes)
{
  target_verse = last_measured + rGrammes;
  Serial.print("INF: verse_quantite: current: ");
  Serial.print(last_measured);
  Serial.print(", target: ");
  Serial.println(target_verse);
  digitalWrite(VANNE_1_PIN, LOW);
}

int check_if_must_stop_verse()
{
  // return 0 if not versing, 1 if versing, 2 if done
  if(target_verse<-1000)
  {
    return 0;
  }
  float diff = target_verse-last_measured;
  Serial.print("INF: check_if_must_stop_verse: diff: ");
  Serial.println(diff);
  lcd.print(" => ");
  lcd.print(diff);
  if(diff<1+4) // couramment on prend 5 apres coupure
  {
    digitalWrite(VANNE_1_PIN, HIGH);
    if(0)
    {
      // fait un petit on/off pour bien la fermer (non ca marche pas)
      delay(100);
      digitalWrite(VANNE_1_PIN, LOW);
      delay(100);
      digitalWrite(VANNE_1_PIN, HIGH);
    }
    
    Serial.print("INF: check_if_must_stop_verse: finished, target was ");
    Serial.println(target_verse);
    target_verse = -1001;
    return 2;
  }
  return 1;
}

void force_stop_verse()
{
  Serial.println("INF: force stop verse");
  digitalWrite(VANNE_1_PIN, HIGH);
  target_verse = -1001;
}

#define LEN_COMMAND_MAX 32
char lastCommand[LEN_COMMAND_MAX+1] = "\0";

int handleSerialCommand()
{
  // receive command using the form ##cmd
  // return 1 if a new command has been received
  char command[LEN_COMMAND_MAX];
  int ichar = 0;
  while( Serial.available() && ichar < LEN_COMMAND_MAX )
  {
    command[ichar] = Serial.read();
    if(command[ichar] != '\n')
    {
      Serial.print("DBG: handleSerialCommand: received: ");
      Serial.print( command[ichar] );
      Serial.print( ", 0x" );
      Serial.println( command[ichar], HEX );
      ++ichar;
    }
  }
  if(command[0] != '#')
  {
    return 0;
  }
  if(strncmp(command,lastCommand,ichar))
  {
    // new command
    strncpy(lastCommand,command,ichar);
    lastCommand[ichar] = '\0';
    Serial.print("DBG: handleSerialCommand: new command received: ");
    Serial.println( lastCommand );
    return 1;
  }

  return 0;
}

void sendSerialCommand()
{
  Serial.print("##coucou/1/2/3/");
  //char buf[32];
  //snprintf
  Serial.println(millis());
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
    float reading = scale.get_units(2); // chaque mesure en plus, c'est prend 88ms
    last_measured = reading;
    if(1)
    {
      Serial.print(millis());
      Serial.print(", weight: ");
      Serial.print(reading);
      Serial.print(" => ");
      Serial.print(int(round(reading)));
      Serial.println(" g");
    }

    lcd.home();
    lcd.print(int(round(reading)));
    lcd.print(" g");

    if(check_if_must_stop_verse()==2)
    {
      sendSerialCommand();
    }

    if(0)
    {
      long raw = scale.read_average();
      Serial.print("Result raw avg: ");
      Serial.println(raw);
    }
    if(1)
    {
      //Serial.println("press key to change calibration factor");
      if(Serial.available())
      {
        char input = Serial.read();
        Serial.print("simple letter received: ");
        Serial.println(input);
        if(input == 'a'){ calibration_factor += 100; }
        else if(input == 'z'){  calibration_factor -= 100; }
        else if(input == 's'){  calibration_factor += 10; }
        else if(input == 'x'){  calibration_factor -= 10; }
        else if(input == 'd'){  calibration_factor += 1; }
        else if(input == 'c'){  calibration_factor -= 1; }
        else if(input == 'r'){  calibration_factor = 1; }
        else if(input == 't'){  Serial.println("re-taring..."); scale.tare();}
        else if(input == 'v'){  digitalWrite(VANNE_1_PIN, LOW); delay(1000); digitalWrite(VANNE_1_PIN, HIGH);	 } // a bit of
        else if(input == '1'){  verse_quantite(10);	 } // asservissement sur poids
        else if(input == '2'){  verse_quantite(20);	 }
        else if(input == '3'){  verse_quantite(50);	 }
        else if(input == '4'){  verse_quantite(100); }
        else if(input == '5'){  verse_quantite(200); }
        else if(input == 'f'){  force_stop_verse();	 } // force stop verse
        if(handleSerialCommand())
        {
          lcd.setCursor(0, 1);
          lcd.print(lastCommand);
        }
      }
    }
  }
  delay(100); // en tout, ca loop actuel prend a peu pres 176ms (avec un getunits de 2)
}
#include "HX711.h" // install in the library manager the HX711 by Rob Tillart (for cell amplifier)
#include <LiquidCrystal.h>

# define ASSERT(b) __assert((b),"__FUNC__",__FILE__,__LINE__,"");
// handle diagnostic informations given by assertion and abort program execution:
void __assert(int bTest, const char *__func, const char *__file, int __lineno, const char *__sexp) 
{
  if(bTest)
    return
  Serial.println(__func);
  Serial.println(__file);
  Serial.println(__lineno, DEC);
  Serial.println(__sexp);
  Serial.flush();
  abort();
}

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

  //handleOrder("#Assemble_10_20_30"); // to test when not connected to the tablet
}

float last_measured = 0;


// ask to verse x grammes
float target_verse = -1001; // negative when no current
int nCurrentVanne = -1;
unsigned long timeNextQueueOrder = 0; // we want to wait a bit before handling next queue
void verse_quantite(float rGrammes,int nNumVanne)
{
  target_verse = last_measured + rGrammes;
  nCurrentVanne = nNumVanne;
  Serial.print("INF: verse_quantite: cuve: ");
  Serial.print(nCurrentVanne);
  Serial.print(", current: ");
  Serial.print(last_measured);
  Serial.print(", target: ");
  Serial.println(target_verse);
  digitalWrite(VANNE_1_PIN, LOW);
}

int isTargetDefined()
{
  return !(target_verse<-1000);
}
int check_if_must_stop_verse()
{
  // return 0 if not versing, 1 if versing, 2 if done
  if(!isTargetDefined())
  {
    return 0;
  }
  float diff = target_verse-last_measured;
  Serial.print("INF: check_if_must_stop_verse: cuve: ");
  Serial.print(nCurrentVanne);
  Serial.print(", diff: ");
  Serial.println(diff);
  lcd.setCursor(5, 0);
  lcd.print(" => ");
  lcd.print(int(diff));
  lcd.print(" C");
  lcd.print(nCurrentVanne+1);
  lcd.print("  "); // clean eol
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
    timeNextQueueOrder = millis() + 2000; // wait 2 sec so the tuyau se vide avant de passer a la commande d'apres
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

/*
* retrieve int argument in a string, return the number of argumen set
* argument are coded in a string separated by a '_' _arg1_arg2_arg3... 
* eg: toto_10_34_45_10
*/
int retrieveIntArguments(const char* s, int * pDstArg, int nNbrArgMax)
{
  int nNbrArg = 0;
  const char* p = s;
  const char* pstart = NULL;
  while(*p && nNbrArg < nNbrArgMax )
  {
    if(*p=='_')
    {
      if( pstart != NULL )
      {
        pDstArg[nNbrArg] = atoi(pstart); // atoi s'arrete au premier char non decimal
        nNbrArg += 1;
      }
      pstart = p+1;

    }
    ++p;
  }
  // last remainder:
  if( pstart != NULL && nNbrArg < nNbrArgMax )
  {
    pDstArg[nNbrArg]=atoi(pstart);
    nNbrArg += 1;
  }
  return nNbrArg;
}

#define LEN_COMMAND_MAX 32
char lastCommand[LEN_COMMAND_MAX+1] = "\0";

#define LEN_QUEUE_ORDER 5
int queueOrder[LEN_QUEUE_ORDER*2]; // a list of [numcuve,ml,numcuve,ml,...]
int nNbrQueueOrder = 0; // nbr data in queue order (nbr of data pair)

// receive order format #string
// return 0 on error
int handleOrder( const char * command)
{
  Serial.print( "INF: handleOrder: Receiving: " );
  Serial.println( command );

  if(command[1]=='A' && command[2]=='s')
  {
    Serial.println("INF: handleOrder: Assemble." );
    // Assemble
    int args[5];
    int nNbrArgs = retrieveIntArguments(command,args,5);
    if(1)
    {
      // debug
      Serial.print("DBG: handleOrder: " );
      for(int i=0;i<nNbrArgs;++i)
      {
        Serial.print(i);
        Serial.print(": ");
        Serial.print(args[i]);
        Serial.print(", ");
      }
      Serial.println("");
    }

    // add to queue
    if( nNbrQueueOrder > 0 )
    {
      Serial.println("ERR: handleOrder: queue not cleared!" );
      return 0;
    }
    scale.tare(); // remet a zero c'est mieux pour valider la pesée de la bouteille
    last_measured = 0;
    timeNextQueueOrder = millis();
    ASSERT(nNbrArgs<=LEN_QUEUE_ORDER)
    for( int i=nNbrArgs-1; i >= 0; --i )
    {
      if(args[i]>0)
      {
        queueOrder[nNbrQueueOrder*2+0] = i;
        queueOrder[nNbrQueueOrder*2+1] = args[i];
        ++nNbrQueueOrder;
      }
    }
  } // assemble
  else if(command[1]=='O' && command[2]=='n')
  {
    verse_quantite(750,command[4]-'0');
  }
  else if(command[1]=='O' && command[2]=='f')
  {
    force_stop_verse();
  }
  else if(command[1]=='S' && command[2]=='T')
  {
    // STOP
    Serial.println("INF: handleOrder: STOP !" );
    nNbrQueueOrder = 0;
    force_stop_verse();
  } // STOP

  return 1;
}

int handleSerialCommand()
{
  // receive command using the form ##cmd
  // return 1 if a new command has been received
  char command[LEN_COMMAND_MAX];
  int ichar = 0;
  delay(20); // for all characters to arrive at 1200chr/sec => 24 chr
  while( Serial.available() && ichar < LEN_COMMAND_MAX )
  {
    command[ichar] = Serial.read();
    if(command[ichar] != '\n')
    {
      if(0)
      {
        Serial.print("DBG: handleSerialCommand: received: ");
        Serial.print( command[ichar] );
        Serial.print( ", 0x" );
        Serial.println( command[ichar], HEX );
      }
      ++ichar;
    }
  }
  command[ichar]='\0';
  if(command[0] != '#')
  {
    return 0;
  }
  //if(strncmp(command,lastCommand,ichar)) // ce test ne sert a rien! on ne recoit jamais une commande en double par erreur
  if(1)
  {
    // new command
    // attention, certain cas, on recoit 2 commandes a la suite, par exemple #on##off
    // test me in the serial monitor message line, by typing ##On_1##Off_1
    const char * p = command;
    char * d = lastCommand;
    while(*p)
    {
      *d=*p;
      ++d;
      ++p;
      if(*p=='#') // we test here because we don't want to test on the first char
        break;
    }
    
    *d = '\0';
    //Serial.print("DBG: handleSerialCommand: new command received: ");
    //Serial.println( lastCommand );
    handleOrder(lastCommand);
    if(*p=='#')
    {
      // a second command is here
      ++p;
      strcpy(lastCommand,p);
      handleOrder(lastCommand);
    }
    return 1;
  }

  return 0;
}

void sendSerialCommand(const char * msg)
{
  Serial.print("##");
  Serial.println(msg);
  //char buf[32];
  //snprintf
  //Serial.println(millis());
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
    if(0)
    {
      Serial.print(millis());
      Serial.print(", weight: ");
      Serial.print(reading);
      Serial.print(" => ");
      Serial.print(int(round(reading)));
      Serial.println(" g    ");
    }

    lcd.home();
    lcd.print(int(round(reading)));
    lcd.print(" g    ");

    int nResVerse = check_if_must_stop_verse();
    if(nResVerse==2)
    {
      sendSerialCommand("End0"); // +nCurrentVanne
      lcd.clear();
    }
    else if(nResVerse==1)
    {
      sendSerialCommand("Fill0"); // +nCurrentVanne
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
        if(1)
        {
          // manual command
          if(input == 'a'){ calibration_factor += 100; }
          else if(input == 'z'){  calibration_factor -= 100; }
          else if(input == 's'){  calibration_factor += 10; }
          else if(input == 'x'){  calibration_factor -= 10; }
          else if(input == 'd'){  calibration_factor += 1; }
          else if(input == 'c'){  calibration_factor -= 1; }
          else if(input == 'r'){  calibration_factor = 1; }
          else if(input == 't'){  Serial.println("re-taring..."); scale.tare();}
          else if(input == 'v'){  digitalWrite(VANNE_1_PIN, LOW); delay(1000); digitalWrite(VANNE_1_PIN, HIGH);	 } // a bit of
          else if(input == '1'){  verse_quantite(10,0);	 } // asservissement sur poids
          else if(input == '2'){  verse_quantite(20,0);	 }
          else if(input == '3'){  verse_quantite(50,0);	 }
          else if(input == '4'){  verse_quantite(100,0); }
          else if(input == '5'){  verse_quantite(200,0); }
          else if(input == 'd'){  sendSerialCommand("Debug/1/2/3"); } // debug
          else if(input == 'f'){  force_stop_verse();	 } // force stop verse
        }
        if(handleSerialCommand())
        {
          lcd.clear();
          lcd.setCursor(0, 1);
          lcd.print(lastCommand);
        }
      }
    }
    if(1)
    {
      if( nNbrQueueOrder > 0 )
      {
        // handle queue
        if(!isTargetDefined())
        {
          if( millis() >= timeNextQueueOrder )
          {
            --nNbrQueueOrder;
            verse_quantite(queueOrder[nNbrQueueOrder*2+1],queueOrder[nNbrQueueOrder*2+0]);
          }
        }
      }
    }
  }
  delay(100); // en tout, ca loop actuel prend a peu pres 176ms (avec un getunits de 2)
}
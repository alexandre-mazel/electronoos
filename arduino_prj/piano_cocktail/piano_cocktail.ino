#include "HX711.h" // install in the library manager the HX711 by Rob Tillart (for cell amplifier)
#include <LiquidCrystal.h>
#include <EEPROM.h>

# define ASSERT(b) __assert((b),"__FUNC__",__FILE__,__LINE__,"");
// handle diagnostic informations given by assertion and abort program execution:
void __assert(int bTest, const char *__func, const char *__file, int __lineno, const char *__sexp) 
{
  if(bTest)
  {
    return;
  }
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
const int LOADCELL_SCK_PIN = A0; // attention, c'est pas D0 (le TX) mais bien A0 (a coté du Vin) !!!

#endif

HX711 scale;


// ordre de branchement: Rouge (E+) Noir (E-) Blanc  (A-) Vert (A+)
// de l'autre cote: GND, DT, SCK, VCC

// si plus petit, ca surcote un peu (les poids affiché semblent etre plus lourd que la réalité)

// reglage pour la barre de 10kg:

//float calibration_factor = 205; // when set to 1, it's = read/known value // poid de 1kg: 206.9, poid de 20g: 193.68
// avec 200:
// poids de gym, l'un a 1041 et l'autre a 1036
// poids de 20g+10g, entre 29.10 et 29.38
// 
// Mon tel A52s: 226g
// Un steack hache: 100g

// reglage pour barre de 3kg:

float calibration_factor = 742.80; // 30g => 22000: 733 [une bouteille vide (celle de blanc orschwiller) peserait 448g; le plateau en fer 352g]
// will be overwritten by EEPROM reading (so I put 100 to remember and test), to write it goto readCfgFromEeproom

// la balance dans le sous sol: 733
// balance a ochateau, section 1: 733 => 929 au lieu de 1030,cad la bonne valeur est entre 660 et 661 => 661
// balance du oversized: 661 => 1140 au lieu de 1030/1036, mettre entre 727 et 732 => mettre 729

// Balance numero 4 (futur nouvel assembleur B): 742.80
// Balance numero 5 (futur nouvel assembleur A): 673.86

float old_calibration_factor = calibration_factor;


/*
long read_average(byte times = 10); // Average 'times' raw readings
double get_value(byte times = 1); // return read_average(times) - OFFSET
float get_units(byte times = 1); // return get_value(times) / SCALE;
void tare(byte times = 10); // OFFSET = read_average(times);

So, get_units() returns (read_average(1) - OFFSET) / SCALE;
*/

const int VANNE_1_PIN = 32; // others need to be continuous
const int NBR_VANNE = 5;

const int VANNE_TEST_PIN = 44;


#include <LiquidCrystal_I2C.h>

bool i2CAddrTest(uint8_t addr) {
  Wire.begin();
  Wire.beginTransmission(addr);
  if (Wire.endTransmission() == 0) {
    return true;
  }
  return false;
}

// initialize the library with the numbers of the interface pins
LiquidCrystal_I2C * pLcd = NULL;

int nAnimateLcdCount = 0;
void animateLcd()
{
  const int nNbrAnimateMax = 3;
  nAnimateLcdCount += 1;
  if( nAnimateLcdCount > nNbrAnimateMax )
  {
    nAnimateLcdCount = 0;
  }
  for( int i = 0; i < nAnimateLcdCount; ++i )
  {
    pLcd->print(".");
  }
  for( int i = nAnimateLcdCount; i < nNbrAnimateMax; ++i )
  {
    pLcd->print(" ");
  }
}

long int nTimeStartFill = 0;
int bIsFilling = 0;

unsigned char nMilliBeforeCut = 70; // 10 en version normal (maintenant 13), en oversize: 45 si slow, si rapide, mettre 100, et mettre

bool bIsOversize = 1;

bool bActivateHache  = bIsOversize; // activate on oversized

int nWaitBetweenBottleMs = 1000; // was 5000, then 3000 (new: doubled when oversize)

unsigned long hache_timeNextChange = 0;
int hache_nNextIsOpen = 1;
int hache_period_ms = 500;

// internal opening, without high level handling
void _setOpen( int nNumVanne, int bOpen)
{
    digitalWrite(VANNE_1_PIN+nNumVanne, bOpen?LOW:HIGH); // high don't send voltage => HIGH is OFF.
}

void setOpen( int nNumVanne, int bOpen)
{ 
    // ouvre ou ferme la vanne.
    // - nNumVanne: 0..n-1
    // - bOpen: 1: ouvre, 0: ferme

    _setOpen(nNumVanne, bOpen);
    
    
    // we will hache only if versing is on, so next hache will be after an opening
    hache_nNextIsOpen = 0;

    int nHacheTime = hache_period_ms;
    if( bOpen )
      nHacheTime /= 2; // we hache half the wait time

    hache_timeNextChange = millis()+nHacheTime;


    if(bOpen)
    {
      nTimeStartFill = millis();
      bIsFilling = true;
    }
    else
    {
      bIsFilling = false;
    }
}

void readCfgFromEeproom()
{
  if(1)
  {
    //write values (for the first time)
    Serial.println("\nWRITING TO EEPROM !\n");
    EEPROM.put(0x00, calibration_factor);
    EEPROM.put(0x04, nMilliBeforeCut);
    
  }

  EEPROM.get(0x00, calibration_factor);
  EEPROM.get(0x04, nMilliBeforeCut);
  //nMilliBeforeCut = 120;
}

void setup() {
  
  Serial.begin(57600); // was 9600 // changing here need to change also in the android application.
  //pinMode(resetPin, INPUT);

  Serial.println("\nPianoCocktail v0.91");

  for( int i = 0; i < NBR_VANNE; ++i )
  {
    pinMode(VANNE_1_PIN+i, OUTPUT);
  }

  pinMode(VANNE_TEST_PIN, OUTPUT);
  digitalWrite(VANNE_TEST_PIN, HIGH);

  close_all();

  uint8_t i2cAddr = 0x3F;
  if(!i2CAddrTest(i2cAddr))
  {
    i2cAddr = 0x27;
  }

  Serial.print("DBG: Using LCD at I2C Addr: 0x");
  Serial.println(i2cAddr,HEX);

  pLcd = new LiquidCrystal_I2C(i2cAddr, 16, 2); // 0x3F sur la version de base, 0x27 sur la version oversized
  
  pLcd->init();                // initialize the lcd
  pLcd->backlight();           // Turn on backlight // sans eclairage on voit rien...
  //pLcd->noBacklight();
  // pLcd->setBacklight(2);

  pLcd->print("Setup started...");

  readCfgFromEeproom();
  
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  while(!scale.is_ready())
  {
    Serial.println("INF: Waiting for HX711...");
    delay(500);
    pLcd->setCursor(0, 0);
    pLcd->print("HX711 waiting");
    animateLcd();
  }
  pLcd->clear();
  pLcd->setCursor(0, 0);
  pLcd->print("taring...");
  Serial.print("calibration_factor: ");
  Serial.println(calibration_factor);
  scale.set_scale(calibration_factor);
  scale.tare();                           // reset weight on scale to 0 grams
  delay(500);
  long zero_factor = scale.read_average();
  Serial.print("Zero factor: ");
  Serial.println(zero_factor);
  delay(500);
  pLcd->clear();
  
  // print all eeproms read parameters
  Serial.print("nMilliBeforeCut: ");
  Serial.println(nMilliBeforeCut);

  //handleOrder("#Assemble_10_20_30"); // to test when not connected to the tablet

  if( bIsOversize )
  {
    nWaitBetweenBottleMs *= 2;
  }

} // setup

float last_measured = 0;
float rTotalTarget = -1; // set when we receive an assemble command to fill the bottle to the brim - or not more



// ask to verse x grammes
float target_verse = -1001; // negative when no current
int nCurrentVanne = -1;
unsigned long timeNextQueueOrder = 0; // we want to wait a bit before handling next queue
float rCurrentQuantityToVerse = -1;

float rPrevLastMeasured = -1;
int nCptFrameWithNoChangeInWeight = 0;

int nbBalanceIsStuck = 0;
unsigned long timeLastBalanceStuck = 0;

void verse_quantite(float rGrammes,int nNumVanne)
{
  target_verse = last_measured + rGrammes;
  rCurrentQuantityToVerse = rGrammes;
  nCurrentVanne = nNumVanne;
  Serial.print("INF: verse_quantite: cuve: ");
  Serial.print(nCurrentVanne);
  Serial.print(", current: ");
  Serial.print(last_measured);
  Serial.print(", target: ");
  Serial.println(target_verse);
  setOpen(nNumVanne,1);
}

void hache()
{
    // handle the fact we want to slow down filling by making the opening clignote every 500ms
    
    if( millis() > hache_timeNextChange )
    {
        Serial.println("haching...");
        _setOpen(nCurrentVanne,hache_nNextIsOpen);
        hache_nNextIsOpen ^= 1; // pingpong between 0 and 1
        hache_timeNextChange = millis() + hache_period_ms;
    }
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
  pLcd->setCursor(5, 0);
  pLcd->print(" => ");
  pLcd->print(int(diff));
  pLcd->print(" C");
  pLcd->print(nCurrentVanne+1);
  pLcd->print("  "); // clean eol
  
  pLcd->setCursor(4, 1);
  //pLcd->print("dbg: ");
  pLcd->print(rCurrentQuantityToVerse);
  if( rTotalTarget > 0.f)
  {
    pLcd->print( "/" );
    pLcd->print(rTotalTarget);
  }

  if( abs(last_measured - rPrevLastMeasured) < 0.5 )
  {
    // c'est en train de verser, et ca bouge pas alors qu'on a un asservissement en poids.
    // c'est mauvais signe!

    Serial.print("INF: Balance is stuck ? rPrevLastMeasured: "); Serial.print( rPrevLastMeasured ); Serial.print( ", last_measured: " ); Serial.print( last_measured ); Serial.print( ", nCptFrameWithNoChangeInWeight: " ); Serial.println( nCptFrameWithNoChangeInWeight );

    ++nCptFrameWithNoChangeInWeight;
    if( nCptFrameWithNoChangeInWeight > 10 ) // roughly 2sec
    {
      nCptFrameWithNoChangeInWeight = 0;
      Serial.println("INF: Balance seems stuck !");
      nbBalanceIsStuck = 1;
      timeLastBalanceStuck = millis();
    }
    else
    {
      nbBalanceIsStuck = 0; // let's reset it to leave a chance to some wine to be send
    }
  }
  else
  {
    rPrevLastMeasured = last_measured;
    nCptFrameWithNoChangeInWeight = 0;
    nbBalanceIsStuck = 0;
  }

  
  
  if(diff<nMilliBeforeCut || nbBalanceIsStuck) // couramment on prend 8 apres coupure // On ajoute 1 de plus en condition réél des caves
  {
    setOpen(nCurrentVanne, 0);
    if(0)
    {
      // fait un petit on/off pour bien la fermer (non ca marche pas)
      delay(100);
      setOpen(nCurrentVanne, 1);
      delay(100);
      setOpen(nCurrentVanne, 0);
    }
    
    Serial.print("INF: check_if_must_stop_verse: finished, target was ");
    Serial.println(target_verse);
    target_verse = -1001;
    timeNextQueueOrder = millis() + nWaitBetweenBottleMs; // wait some sec so the tuyau se vide avant de passer a la commande d'apres
    return 2;
  }
  
  // hachage en fin de versage
  if(rTotalTarget < 0 && diff < 300 && bActivateHache ) // if it's the last cuve, and near the end, we must slow down
  {
    hache();
  }
  return 1;
}

void close_all()
{
  Serial.println("INF: close_all");
  for( int i = 0; i < NBR_VANNE; ++i )
  {
    setOpen(i, 0);
  }
}

void force_stop_verse()
{
  Serial.println("INF: force stop verse !");
  close_all();
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


void stop_all()
{
  force_stop_verse(); 
  nNbrQueueOrder = 0;
}

void chenillard()
{
  Serial.println("INF: chenillard");
  delay(1000);
  for( int j = 0; j < 5; ++j )
  {
    Serial.println("INF: chenillard: looping...");
    for( int i = 0; i < NBR_VANNE; ++i )
    {
      setOpen(i, 1);
      delay(1000);
      setOpen(i, 0);
      delay(1000);
    }
  }
  Serial.println("INF: chenillard - end ");
}

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
    rTotalTarget = 0;
    timeNextQueueOrder = millis();
    ASSERT(nNbrArgs<=LEN_QUEUE_ORDER)
    for( int i=nNbrArgs-1; i >= 0; --i )
    {
      if(args[i]>0)
      {
        queueOrder[nNbrQueueOrder*2+0] = i;
        queueOrder[nNbrQueueOrder*2+1] = args[i];
        rTotalTarget += args[i];
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
    stop_all();
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

char dummyChangeCompiledSizeToPreventUploadError[23] = {1,2};

void simulateReceiveAssembleOrder( int qt1 = 50, int qt2 = 50, int qt3 = 50, int qt4 = 50, int qt5 = 50)
{
  Serial.println("simulateReceiveAssembleOrder");
  scale.tare();
  int aqt[NBR_VANNE] = {qt1,qt2,qt3,qt4,qt5};
  nNbrQueueOrder = 0;
  for(int i = NBR_VANNE-1; i >= 0; --i )
  {
    queueOrder[nNbrQueueOrder*2+0] = i;
    queueOrder[nNbrQueueOrder*2+1] = aqt[i];
    ++nNbrQueueOrder;
  }
  timeNextQueueOrder = millis() + 500;
}

int bWasDisconnected = 0;

void loop() 
{

  // security
  if(bIsFilling && millis()-nTimeStartFill>60*1000L) // 60*1000 => 1 min
  {
    // 1 min => security close
    stop_all();
    pLcd->home();
    Serial.println("WRN: Security close!");
    pLcd->print("Security close!");
    delay(5000);
  }
  
  
  if (!scale.is_ready()) 
  {
    Serial.println("HX711 not found.");
    pLcd->home();
    pLcd->print("HX711: Disconnected");
    //close_all();
    bWasDisconnected = 1;
    delay(500);
  }
  else
  {
    if(bWasDisconnected)
    {
      Serial.println("DBG: was disconnected");
      pLcd->clear();
      bWasDisconnected = 0;
    }
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
    float reading = scale.get_units(2); // chaque mesure en plus, c'est 88ms
    if( reading > 3000 )
    {
      Serial.print("WRN: weird reading (keeping previous): ");
      Serial.println("reading ");
      reading = last_measured;
    }
    else
    {
      last_measured = reading;
    }

    if(1)
    { 
      Serial.print( "DBG: " );
      Serial.print(millis());
      Serial.print(", weight: ");
      Serial.print(reading);
      Serial.print(" => ");
      Serial.print(int(round(reading)));
      Serial.println(" g    ");
    }

    pLcd->home();
    pLcd->print(int(round(reading)));
    pLcd->print(" g    ");

    int nResVerse = check_if_must_stop_verse();
    if(nResVerse==2)
    {
      sendSerialCommand("End0"); // +nCurrentVanne
      pLcd->clear();
    }
    else if(nResVerse==1)
    {
      sendSerialCommand("Fill0"); // +nCurrentVanne
    }

    if( nbBalanceIsStuck )
    {     
      pLcd->setCursor(0, 1);
      pLcd->print("ERR: Bal stuck?");

      if(millis()-timeLastBalanceStuck>3000)
      {
        // let's check it moved again (the goal is to remove the error about the stuck balance)
        Serial.print("INF: balance stiistuck ? last_measured:"); Serial.println(last_measured);
        if( abs(last_measured - rPrevLastMeasured) > 10 )
        {
          nbBalanceIsStuck = 0;
          pLcd->clear(); // clear msg
        }
      }
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
          else if(input == 'V'){  Serial.println("vanne de test"); digitalWrite(VANNE_TEST_PIN, LOW); delay(1000); digitalWrite(VANNE_TEST_PIN, HIGH);	 } // une vanne de test
          else if(input == '1'){  verse_quantite(10,0);	 } // asservissement sur poids
          else if(input == '2'){  verse_quantite(20,0);	 }
          else if(input == '3'){  verse_quantite(50,0);	 }
          else if(input == '4'){  verse_quantite(100,0); }
          else if(input == '5'){  verse_quantite(200,0); }
          else if(input == 'A'){  simulateReceiveAssembleOrder(); }
          else if(input == 'd'){  sendSerialCommand("Debug/1/2/3"); } // debug
          else if(input == 'f'){  force_stop_verse();	 } // force stop verse
          else if(input == 'S'){  stop_all();} // Stop All
          else if(input == 'C'){  chenillard();} // one each second
        }
        if(handleSerialCommand())
        {
          pLcd->clear();
          pLcd->setCursor(0, 1);
          pLcd->print(lastCommand);
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
            Serial.println("DBG: Processing next order...");
            --nNbrQueueOrder;
            float rGramme = queueOrder[nNbrQueueOrder*2+1];
            if(nNbrQueueOrder==0 && rTotalTarget>0)
            {
              rGramme = rTotalTarget-last_measured-0.5; // remove 0.5g to add margin car bouteille trop pleine
              rGramme -= 5; // 2024/08/27: enleve 5g sur le total car ca fait trop sur le petit assembleur (la balance perdrait des grammes genre 10g a la minute ce qui explique le débordement?)
              rTotalTarget = -1;
            }
            if(rGramme>0)
            {
              verse_quantite(rGramme,queueOrder[nNbrQueueOrder*2+0]);
            }
          }
        }
      }
    }
  }
  delay(100); // en tout, ca loop actuel prend a peu pres 176ms (avec un getunits de 2)
}
/*

Objective:
- Drive 3 stepper motors at the same time with various speed.
- Receive command from Serial2

If you want to test me, by sending manual command to the serial:
1) define the GET_ORDER_FROM_SERIAL1 to read orders from serial1 instead of serial2 (normal use)

2) send command from the serial monitor input field (at 57600):
// launch the first motor at 10 rpm
##MOTOR_0_1_10
// launch the first motor in reverse mode at 50 rpm
##MOTOR_0_-1_50
// stop it
##MOTOR_0_0_0
*/

#include "steppers_driver.hpp"


#define GET_ORDER_FROM_SERIAL1 // to debug with command from default serial

 #ifdef GET_ORDER_FROM_SERIAL1
  #define SERIAL_ORDER Serial
#else
  #define SERIAL_ORDER Serial2
#endif

#define DEBUG Serial
unsigned long fpsTimeStart = 0;
unsigned long fpsCpt = 0;
unsigned long nFrameMsMin = 4000;
unsigned long nFrameMsMax = 0;
unsigned long fpsTimeLast = 0;

#define enaPin 37 //enable-motor
#define dirPin 38 //direction
#define stepPin 39 //step-pulse

// twist
#define enaPin2 27 //enable-motor
#define dirPin2 28 //direction
#define stepPin2 29 //step-pulse

#define stepPin2_pwm 4 //step-pulse 4: pwm a 976Hz, 5: pwm a 490Hz


// collect
#define enaPin3 41 //enable-motor
#define dirPin3 43 //direction
#define stepPin3 45 //step-pulse

#define pin_switchContact 50


void countFps()
{
  fpsCpt += 1;

  // optim: don't read millis at everycall
  // gain 1.1micros per call (averaged)
  // an empty loop takes 67.15micros on mega2560 (just this function)
  if((fpsCpt&7)!=7 && 0)
  {
    return;
  }  

  if(1)
  {
    // count min and max frame
    unsigned long diff = millis() - fpsTimeLast;
    if( diff > nFrameMsMax )
    {
      nFrameMsMax = diff;
    }
    if( diff < nFrameMsMin )
    {
      nFrameMsMin = diff;
    }
    fpsTimeLast = millis();
  }

  unsigned long diff = millis() - fpsTimeStart;
  if (diff > 5000)
  {
    //unsigned long timeprintbegin = micros();
    float fps = (float)(fpsCpt*1000)/diff;
    DEBUG.print("fps: ");
    DEBUG.print(fps);
    DEBUG.print(", dt: ");
#if 1
    {
      DEBUG.print(1000.f/fps,3);
      DEBUG.println("ms");
    }
#else
    {
      DEBUG.print(1000000.f/fps);
      DEBUG.println("micros");
    }
#endif
#if 1
    {
      DEBUG.print("dt min/max: ");
      DEBUG.print(nFrameMsMin);
      DEBUG.print(" / ");
      DEBUG.print(nFrameMsMax);
      DEBUG.println("ms");

      nFrameMsMin = 10000;
      nFrameMsMax = 0;
    }
#endif

    fpsTimeStart = millis();
    fpsCpt = 0;
    //unsigned long durationprint = micros()-timeprintbegin;
    //DEBUG.print("duration fps micros: "); // 1228micros at 57600baud !!!, 1280 at 115200 (change nothing, it's more the time to compute)
    //DEBUG.println(durationprint);
  }

}

SteppersDriver steppersDriver(3);

void setup() 
{
  Serial.begin(57600);
  Serial.println("");
  Serial.println("Bobin Filler v0.6");

  SERIAL_ORDER.begin(57600);
  
  const int nStepPerRevolution = 200;

  steppersDriver.setup(0,enaPin,dirPin,stepPin,nStepPerRevolution);
  steppersDriver.setup(1,enaPin2,dirPin2,stepPin2,nStepPerRevolution);
  steppersDriver.setup(2,enaPin3,dirPin3,stepPin3,nStepPerRevolution);
  steppersDriver.initPins();

  pinMode( pin_switchContact, INPUT );  
}

int isIntChar(const char c)
{
  return (c >= '0' && c <= '9') || c == '-' || c == '+';
}

/*
* retrieve int argument in a string, return the number of argument set
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
        // on a des fois des parasites et donc la commande est pétée! (par exemple on recoit ':' a la place du nombre ou X ou ...)
        if(isIntChar(*pstart))
        {
          int val = atoi(pstart); // atoi s'arrete au premier char non decimal
          pDstArg[nNbrArg] = val;
        }
        else
        {
          pDstArg[nNbrArg] = -666;
        }
        nNbrArg += 1;
      }
      pstart = p+1;

    }
    ++p;
  }
  // last remainer:
  if( pstart != NULL && nNbrArg < nNbrArgMax )
  {
    if(isIntChar(*pstart))
    {
      pDstArg[nNbrArg]=atoi(pstart);
    }
    else
    {
      pDstArg[nNbrArg] = -666;
    }
    nNbrArg += 1;
  }
  return nNbrArg;
}

void updateMotorCommand()
{
  steppersDriver.update();
}



#define LEN_COMMAND_MAX 32
char lastCommand[LEN_COMMAND_MAX+1] = "\0";

// receive order format #string
// return 0 on error
int handleOrder( const char * command)
{
  int bDebug = 1;
  bDebug = 0;

  // this two next lines takes: 356us
  if(bDebug)
  {
    //int before = micros();
    Serial.print( "INF: handleOrder: Receiving: " );
    Serial.println( command );
    //defore = micros()-before;
    //Serial.println(before);
  }


  if(command[2]=='M' && command[3]=='O')
  {
    if(bDebug) Serial.println("INF: handleOrder: Command: Motor" );
    // Assemble
    int args[3];
    int nNbrArgs = retrieveIntArguments(command,args,3);
    if(bDebug)
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
    } // debug

    // consistency check (souvent quand les 2 Arduinos ne sont pas alimenté par la meme source)
    if( args[0] < 0 || args[0] > 2 || args[1] < -1 || args[1] > 1 || args[2] < 0)
    {
      Serial.println("WRN: Rotten orders, skipping!");
    }
    else
    {
      steppersDriver.order(args[0],args[1],args[2]);
    }
  } // if command

  return 1;
}

int handleSerialCommand()
{
  // receive command using the form ##cmd__param1__param2__param3
  // return 1 if a new command has been received

  if(!SERIAL_ORDER.available())
  {
    return 0;
  }

  char command[LEN_COMMAND_MAX];
  int ichar = 0;
  delay(5); // for all characters to arrive at 57600 baud, 7200chr/sec => donc pour 32 chr => 225 commands/sec, soit 4.4ms pour une commande complete
  while( SERIAL_ORDER.available() && ichar < LEN_COMMAND_MAX )
  {
    command[ichar] = SERIAL_ORDER.read();
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
      if(*p=='#' && p-command>2) // we test here because we don't want to test on the first char
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
  Serial2.print("##");
  Serial2.println(msg);
  //char buf[32];
  //snprintf
  //Serial.println(millis());
}

const int kPhaseInit = 0;       // what we do first
const int kPhasePutToGuide = 1; // first put the guide to the push contact button
const int kPhaseFill = 2;
int nPhase = kPhaseInit; // phase

long int nPrevNumEvent = -1;
long int nCptBeforeNextEvent = -1;
char szNextCommand[256];
void loop() 
{
  handleSerialCommand(); // takes around 2micros (when no command)
  updateMotorCommand(); // takes around 5micros (when no motors running)
  //countFps();
  //delay(1);

  if( nPhase == kPhaseInit )
  {
    handleOrder( "##MOTOR_1_1_240" ); // start the motor to the bumper
    nPhase = kPhasePutToGuide;
  }
  else if( nPhase == kPhasePutToGuide )
  {
    int nPushed = digitalRead( pin_switchContact );
    Serial.print( "INF: current push button: " ); Serial.println( nPushed );
    if( nPushed )
    {
      handleOrder( "##MOTOR_1_0_0" );
      nPhase = kPhaseFill;
    }
  }
  else
  {
    return;

    long int nNumEvent = millis() / 1100;
    if( nPrevNumEvent != nNumEvent )
    {
      nPrevNumEvent = nNumEvent;
      Serial.print( "nNumEvent: " ); Serial.println( nNumEvent );

      handleOrder( "##MOTOR_1_1_100" );

      if( nNumEvent % 2 == 0 )
      {
        handleOrder( "##MOTOR_0_0_0" );
        strcpy( szNextCommand, "##MOTOR_0_1_380" );
        nCptBeforeNextEvent = 1000;
      }
      else
      {
        handleOrder( "##MOTOR_0_0_0" );
        strcpy( szNextCommand, "##MOTOR_0_-1_380" );
        nCptBeforeNextEvent = 1000;
      }
    }
    if( nCptBeforeNextEvent >  0 )
    {
      --nCptBeforeNextEvent;
      if( nCptBeforeNextEvent == 0 )
      {
        handleOrder( szNextCommand );
      }
    }
  } // else case
}
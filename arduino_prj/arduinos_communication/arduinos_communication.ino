#define DEBUG Serial
unsigned long fpsTimeStart = 0;
unsigned long fpsCpt = 0;
unsigned long nFrameMsMin = 4000;
unsigned long nFrameMsMax = 0;
unsigned long fpsTimeLast = 0;

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

StepperDriver stepperDriver(3);

void setup() 
{
  Serial.begin(57600);
  Serial.println("");
  Serial.println("Receive Command v0.6");

  Serial2.begin(57600);
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

void updateMotorCommand()
{
  stepperDriver.update();
}



#define LEN_COMMAND_MAX 32
char lastCommand[LEN_COMMAND_MAX+1] = "\0";

// receive order format #string
// return 0 on error
int handleOrder( const char * command)
{
  int bDebug = 1;

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
    Serial.println("INF: handleOrder: Command: Motor" );
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
  } // if command

  return 1;
}

int handleSerialCommand()
{
  // receive command using the form ##cmd__param1__param2__param3
  // return 1 if a new command has been received

  if(!Serial2.available())
  {
    return 0;
  }

  char command[LEN_COMMAND_MAX];
  int ichar = 0;
  delay(5); // for all characters to arrive at 57600 baud, 7200chr/sec => donc pour 32 chr => 225 commands/sec, soit 4.4ms pour une commande complete
  while( Serial2.available() && ichar < LEN_COMMAND_MAX )
  {
    command[ichar] = Serial2.read();
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


void loop() 
{
  handleSerialCommand();
  updateMotorCommand();
  countFps();
  delay(10);
}
// Handle BJY61 angle reading on an arduino using serial3 for read and serial0 for debug
// v0.6
// based on: https://www.scribd.com/document/276841798/JY-61-MPU6050-module-User-Manual-by-Elecmaster
// bought from: https://www.amazon.fr/gp/product/B01LXXHUDR/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1

int incomingByte = 0;   // for incoming serial data

const int nNbrSensor = 3;

HardwareSerial hs[] = {Serial1, Serial2, Serial3};

byte aaTrame[nNbrSensor][20]; // for each sensor
int anTrameLen[nNbrSensor] = {0,0,0};
int anTrameStatus[nNbrSensor] = {0,0,0}; // -1: ?, 0: waiting for first mark, 1: waiting for 2nd start mark, 2: in the trame
int anLastX[nNbrSensor] = {0,0,0};
int nCptFrame = 0;
unsigned long timeLastOutput = 0;

void setup()
{
  
    Serial.begin(9600); // Not only for debug, but also for external communication
    
    Serial.println("DBG: Opening port...");
    for( int i = 0; i < nNbrSensor; ++i )
    {
      hs[i].begin(115200);
    }
    Serial.println("DBG: Open...");   
 
   // send command
   if( 1 )
   {  
      for( int i = 0; i < nNbrSensor; ++i )
      {
         // force a Z axis zero reset
         hs[i].write( 0XFF );
         hs[i].write( 0XAA );
         hs[i].write( 0X52 );
      }
   }
 
   Serial.println("DBG: Running...");      
}

void printBuf( byte * pTrame, int len )
{
  int i;
  Serial.print( "buf: " );
  for( i = 0; i < len; ++i )
  {
    Serial.print( pTrame[i], HEX );
    Serial.print( " " );
  }
  Serial.println("");
}

void analyse( int nNumSensor, byte * pTrame, int len )
{
  
  short int aX = ((short) (pTrame[1]<<8|pTrame[0]))/32768.0*1800; // // add a x10 to see difference (peut etre qu'un x8 serait plius précis) 
  short int aY = ((short) (pTrame[3]<<8|pTrame[2]))/32768.0*1800;
  short int aZ = ((short) (pTrame[5]<<8|pTrame[4]))/32768.0*1800;  
  short int t =  ((short) (pTrame[7]<<8|pTrame[6]))/34.0+365.30; // 13 when at 8, <2 when at -18 (also seen: +36.25)
                                                                 // 26 when at 26, but then 33: the sensor should arise by itself
                                                                 
  anLastX[nNumSensor] = aX;
  if( 0 )
  {
    Serial.print( "# " );                                                                 
    Serial.print( millis(), DEC );
    Serial.print( ": " );  
    Serial.print( nNumSensor, DEC );
    Serial.print( ": " );
    for( int i = 0; i < nNumSensor; ++i )
    {
      Serial.print( "                    " );
    }
    Serial.print( aX, DEC );
    Serial.print( ", " );
    Serial.print( aY, DEC );
    Serial.print( ", " );
    Serial.print( aZ, DEC );
    Serial.print( ", " );  
    Serial.print( t, DEC );
    Serial.println( "." );    
  }
}

byte computeChecksum( byte * pTrame, int len )
{
  int i;
  byte crc = 0; // will explode, it's the goal
  for( i = 0; i < len; ++i )
  {
    crc += pTrame[i];
  }
  return crc;
}

void receiveBytes(int nNumSensor, signed short s)
{
  // it looks like (in hex):
  // 55 51 ax_lo ax_hi ay_lo ay_hi az_lo az_hi temp_lo temp_hi checksum; 55 52 and 55 53 are headers for angular velocity and total angle, respectively.
  
  // 55 53 RollL RollH PitchL PitchH YawL YawH TL TH Checksum
  // Roll 
  //   x axis: Roll=((RollH<<8)|RollL)/32768*180(°) Pitch
  //   y axis: Pitch=((PitchH<<8)|PitchL)/32768*180(°) Yaw
  //   z axis: Yaw=((YawH<<8)|YawL)/32768*180(°) 
  // Temperature calculated formular: T=((TH<<8)|TL) /340+36.53 ℃
  
  // Checksum：Sum=0x55+0x53+RollH+RollL+PitchH+PitchL+YawH+YawL+TH+TL  
  
  const int bDebug = 0;

  
  const int nTrameSize = 8;
  const byte startMark[] = {0x55, 0X53};

  if( anTrameStatus[nNumSensor] < 2 )
  {
    if( s == startMark[anTrameStatus[nNumSensor]] )
    {
      ++anTrameStatus[nNumSensor];
    }
    else
    {
      //Serial.println(".");
      anTrameStatus[nNumSensor] = 0;
    }
  }
  else if( anTrameStatus[nNumSensor] == 2 )
  {
    if( anTrameLen[nNumSensor] == nTrameSize )
    {
      if( bDebug )
      {
        Serial.println( "trame finite" );
        printBuf( aaTrame[nNumSensor], anTrameLen[nNumSensor] );
      }
      
      // s is now the checksum
      byte nComputedCheckSum = computeChecksum( aaTrame[nNumSensor], anTrameLen[nNumSensor] );
      nComputedCheckSum += startMark[0]+startMark[1]; // don't forget to add 55 et 53

      if( bDebug )
      {
        Serial.print("computed crc: 0x");
        Serial.println(nComputedCheckSum, HEX);
        Serial.print("coded crc: 0x");
        Serial.println(s, HEX);      
      }
      
      
      if( nComputedCheckSum == s )
      {
        analyse( nNumSensor, aaTrame[nNumSensor], anTrameLen[nNumSensor] );
      }
      else
      {
        if( bDebug )
        {
          Serial.println( "bad checksum" );
        }
      }
      anTrameStatus[nNumSensor] = 0;
      anTrameLen[nNumSensor] = 0;
    }
    else
    {
      aaTrame[nNumSensor][anTrameLen[nNumSensor]] = s; ++anTrameLen[nNumSensor];
    }
    //Serial.println(s, HEX);
  }
  
}

void loop() 
{
   for( int i = 0; i < nNbrSensor; ++i )
   {
        if( hs[i].available() > 0 )
        {
            // read the incoming byte:
            incomingByte = hs[i].read();
            receiveBytes(i, incomingByte);

            if( 0 )
            {
              // say what you got:
              Serial.print("Sensor");              
              Serial.print(i, DEC);              
              Serial.print(": ");
              Serial.print("received: ");
              Serial.println(incomingByte, DEC);
            }
        }
   }
   ++nCptFrame;
   if( millis() - timeLastOutput > 200 )
   {
      if( 1 )
      {
        Serial.print( "# " );     
        Serial.print( millis(), DEC );
        Serial.print( ", fps: " );
        Serial.println( ((long)nCptFrame * 1000.) / (millis() - timeLastOutput) );
      }
      timeLastOutput = millis();      
      nCptFrame = 0;
      
      Serial.print("XXX");
      for( int i = 0; i < nNbrSensor; ++i )
      {
        // output as a sign and 4 chars: +9999 zeropadded
        short int v = anLastX[i];
        char s = '+';
        if( v < 0 )
        {
          s = '-';
          v = -v;
        }
        Serial.print(s);
        Serial.print(v/1000, DEC);
        v -= (v/1000)*1000;        
        Serial.print(v/100, DEC);
        v -= (v/100)*100;
        Serial.print(v/10, DEC);
        v -= (v/10)*10;        
        Serial.print(v, DEC);
      }
      Serial.println( "" );            
   }
   //delay(0); // fps (outputted every sec): delay(1) => 860fps, delay(0) => 6500fps // pas de delay => 6687fps
}

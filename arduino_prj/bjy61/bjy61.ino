int incomingByte = 0;   // for incoming serial data
byte aTrame[20];
int nTrameLen = 0;
int nTrameStatus = 0; // -1: ?, 0: waiting for first mark, 1: waiting for 2nd start mark, 2: in the trame
void setup() {
  
        Serial.begin(9600);
        Serial.println("DBG: Opening port...");
        Serial3.begin(115200);
        Serial.println("DBG: Open...");        
}

void printBuf( byte * pTrame, int len )
{
  int i;
  Serial.print( "trame to analyse: " );
  for( i = 0; i < len; ++i )
  {
    Serial.print( pTrame[i], HEX );
    Serial.print( " " );
  }
  Serial.println("");
  
  short int a1 = ((short) (pTrame[1]<<8|pTrame[0]))/32768.0*180;
  Serial.println( a1, DEC );  
}

void analyse( byte * pTrame, int len )
{
  int i;
  Serial.print( "trame to analyse: " );
  for( i = 0; i < len; ++i )
  {
    Serial.print( pTrame[i], HEX );
    Serial.print( " " );
  }
  Serial.println("");
  
  short int a1 = ((short) (pTrame[1]<<8|pTrame[0]))/32768.0*180;
  Serial.println( a1, DEC );  
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

void receiveBytes(signed short s)
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

  
  const int nTrameSize = 8;
  const byte startMark[] = {0x55, 0X53};

  if( nTrameStatus < 2 )
  {
    if( s == startMark[nTrameStatus] )
    {
      ++nTrameStatus;
    }
    else
    {
      //Serial.println(".");
      nTrameStatus = 0;
    }
  }
  else if( nTrameStatus == 2 )
  {
    if( nTrameLen == nTrameSize )
    {
      Serial.println("trame finite");
      // s is now the checksum
      byte nComputedCheckSum = computeChecksum( aTrame, nTrameLen ); // don't forget to add 55 et 53
      nComputedCheckSum += startMark[0]+startMark[1];
      printBuf( aTrame, nTrameLen );
      if( nComputedCheckSum == s )
      {
        analyse( aTrame, nTrameLen );
      }
      else
      {
        Serial.println( "bad checksum" );
      }
      nTrameStatus = 0;
      nTrameLen = 0;
    }
    else
    {
      aTrame[nTrameLen] = s; ++nTrameLen;
    }
    //Serial.println(s, HEX);
  }
  
}

void loop() {

        // send data only when you receive data:
        if (Serial3.available() > 0) {
                // read the incoming byte:
                incomingByte = Serial3.read();
                receiveBytes(incomingByte);

                if( 0 )
                {
                  // say what you got:
                  Serial.print("I received: ");
                  Serial.println(incomingByte, DEC);
                }
        }
}

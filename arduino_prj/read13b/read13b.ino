

unsigned char bufPrev[255];
int nBufPrevLen = 0;
unsigned char buf[255];
int nBufLen = 0;

char get_readID[] = { 0xAA , 0x00, 0x03, 0x25, 0x26, 0x00, 0x00, 0xBB };

void setup()
{
  Serial.begin(57600);
  Serial.println("Reading 13 Mhz...");
  Serial1.begin(9600);
  
  // prepare for next read
  for( int counter =0 ; counter < 8 ; counter++)
  {
    Serial1.write(get_readID[counter]);
  }  
}

void loop() // run over and over
{ 
  
  while(Serial1.available())
  {
    // Serial.write( "R" );
    buf[nBufLen] = Serial1.read();
    ++nBufLen;
/*    
    if( buf[nBufLen-1] == 0xBB )
    {
      Serial.println( "BREAK" );
      break; // end of one paquet!
    }
*/    
  }
  if( nBufLen > 0 && buf[nBufLen-1] == 0xBB)
  {
//    Serial.print( "buf[nBufLen-1]: " );    
//    Serial.println( buf[nBufLen-1], HEX );
    
    // ask for a next read
    for( int counter = 0 ; counter < 8 ; counter++)
    {
      Serial1.write(get_readID[counter]);
    }

    if( nBufLen != nBufPrevLen || memcmp( buf, bufPrev, nBufLen ) != 0 )
    {
      Serial.print( "len buf prev: " );
      Serial.print( nBufPrevLen, DEC );
      Serial.print( ", and current: " );    
      Serial.println( nBufLen, DEC );
      
      Serial.write( "Received:" );
      Serial.write( " 0x" );
      for( int i = 0; i < nBufLen; ++i)
      {
        Serial.print( buf[i], HEX );
        Serial.write( " " );
      }  
      Serial.write( "\n" );    
      
      memcpy( bufPrev, buf, nBufLen );
      nBufPrevLen = nBufLen;
    }
    nBufLen = 0;    
  }
  delay( 10 ); 
}

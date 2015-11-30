char buf[255];
int nBufLen = 0;

void setup()
{
  Serial.begin(9600);  
  Serial.println("Reading 13 Mhz...");
  Serial1.begin(9600);    
}

void loop() // run over and over
{ 
//  Serial.println( "." );  
  while(Serial1.available())
  {
    Serial.write( "XX." );
    buf[nBufLen] = Serial1.read();
    ++nBufLen;
  }
  if( nBufLen > 0 )
  {
    Serial.write( "Received:" );
    int i;
    for( i = 0; i < nBufLen; ++i)
    {
      Serial.print( buf[i], DEC );
    }
    Serial.write( " 0x" );
    for( i = 0; i < nBufLen; ++i) // first in 2 and last is 3 => jump it!
    {
      Serial.print( buf[i], HEX );
      Serial.write( " " );
    }  
    Serial.write( "\n" );    
  }
  delay(10);
}

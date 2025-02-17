#include "eeprom_prefs.hpp"


#ifdef USE_PREFS
  Preferences prefs;
#else
#endif // USE_PREFS


void writeStringToEeprom( int nOffsetStart, const char* s )
{
  // write until a '\0' is found in the string

  int nWritten = 0;

#ifdef USE_PREFS
    prefs.begin( "Eeprom" ); // a sort of namespace
    nWritten = strlen( s );
    prefs.putBytes( "Eeprom_mykey", s, nWritten );  // keyname here for compatibility, but it's intended to be a key to have different variables)
#else
  const char * p = s;
  while( *p )
  {
    EEPROM.write(nOffsetStart, *p); // update: write only if different (save a bit of ageing) - changed to write as update seems to be not available
    ++nOffsetStart;
    ++p;
  }
  EEPROM.write(nOffsetStart, *p); // write the null

  EEPROM.commit(); // needed with ESP32 // yes but no => use Prefs

  nWritten = int(p-s);
#endif

  Serial.print( "DBG: writeStringToEeprom: written to eeprom: " );
  Serial.print( nWritten );
  Serial.println( " char(s)" );
}

int readStringFromEeprom( int nOffsetStart, char* s )
{
  int nReaded = 0;

  // read until a '\0' is found in Eeprom
#ifdef USE_PREFS
    prefs.begin("Eeprom");
    nReaded = prefs.getBytesLength("Eeprom_mykey");
    prefs.getBytes("Eeprom_mykey",s,nReaded);
#else
  char * p = s;
  while( 1 )
  {
    char c = EEPROM.read(nOffsetStart);
    *p = c;
    ++nOffsetStart;
    ++p;
    Serial.println((int)c,HEX);
    if( c == '\0' )
    {
      break;
    }
    nReaded = int(p-s);
  }
#endif

  Serial.print( "DBG: readStringFromEeprom: readed from eeprom: " );
  Serial.print( nReaded );
  Serial.println( " char(s)" );

  return nReaded;

}
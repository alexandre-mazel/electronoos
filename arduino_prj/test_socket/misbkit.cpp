#include <arduino.h>
#include "misbkit.hpp"
#include "eeprom_prefs.hpp" // for prefs.putBytes

const char * getArduinoId( void )
{
  // return a 10 letters ID for this Arduino

  static char strName[10+1] = "\0";

  if( strName[0] != '\0' )
    // already inited
    return strName;

  // first time: let's read it from eeprom!
  Serial.println( "INF: getArduinoId: reading ID from Eeprom..." );

#ifdef USE_PREFS
  prefs.begin( "ID" );

  if( 0 )
  {
    // first time: write it!
    // Possible choice: "MisBKit5", "ESP32_C01"
    const char strInitName[] = "MisBKit4"; // should be less than or equal 10 chars
    prefs.putBytes( "Name", strInitName, strlen(strInitName) );
  }

  int strNameLen = prefs.getBytesLength( "Name" );
  prefs.getBytes( "Name", strName, strNameLen );
  strName[strNameLen] = '\0';

#else
  Serial.println( "TODO: in regular EEprom at an offset 0 or random :)" );
#endif

  Serial.print( "INF: getArduinoId: return: " ); Serial.println( strName );

  return strName;

}

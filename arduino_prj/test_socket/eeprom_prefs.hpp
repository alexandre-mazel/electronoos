#ifndef __EEPROM_PREFS_H__
#define __EEPROM_PREFS_H__

#define USE_PREFS // Pref is the new things of esp32


#ifdef USE_PREFS
#   include <Preferences.h>
    extern Preferences prefs;
#else
#    include <EEPROM.h>
#endif // USE_PREFS

void writeStringToEeprom( int nOffsetStart, const char* s );

// return size of readed string
int readStringFromEeprom( int nOffsetStart, char* s );


#endif
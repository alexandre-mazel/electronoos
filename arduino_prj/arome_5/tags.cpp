#include <Arduino.h> // for byte
#include <../../../../libraries/EEPROM/EEPROM.h> // => include here for definition, but include also in the .ino for the link to add the lib



//About eeprom:
// WRN: can't write more than 100000 times. initialised at 0xFF but can change => use a pgm version number

#include "tags.h"

#define NBR_MAGIC_TAG_DIFFERENT 3 // we could have many different memorize tag and ...
char aMagicTagList_Memorize[NBR_MAGIC_TAG_DIFFERENT][TAG_LEN] = 
{
  {0x30, 0x36, 0x30, 0x30, 0x36, 0x46, 0x33, 0x42, 0x32, 0x36, 0x37, 0x34,},
  {0x30, 0x36, 0x30, 0x30, 0x36, 0x45, 0x43, 0x35, 0x37, 0x39, 0x44, 0x34,},  
  {0x30, 0x36, 0x30, 0x30, 0x36, 0x45, 0x43, 0x35, 0x37, 0x30, 0x44, 0x44,},    
};

char aMagicTagList_Forget[NBR_MAGIC_TAG_DIFFERENT][TAG_LEN] = 
{
  {0x30, 0x36, 0x30, 0x30, 0x36, 0x46, 0x34, 0x30, 0x31, 0x46, 0x33, 0x36,},
  {0x30, 0x36, 0x30, 0x30, 0x36, 0x46, 0x33, 0x45, 0x44, 0x37, 0x38, 0x30,},
  {0x30, 0x36, 0x30, 0x30, 0x36, 0x45, 0x37, 0x39, 0x42, 0x43, 0x41, 0x44,},
};




void TagsList_init( TagsList * t )
{
  memset( (void*)t, 0, sizeof( TagsList ) );
}

int TagsList_readFromEprom( TagsList * t, int nOffset )
{
  // read all info from eprom for this taglist
  // return size readed
  int i;
  byte* p = (byte*)t;
  for( i = 0; i < (int)sizeof( TagsList ); ++i)
  {
    (*p) = EEPROM.read( nOffset+i );
    ++p;
  }
  return i;
}

int TagsList_writeToEprom( const TagsList * t, int nOffset )
{
  // store all info to eprom from this taglist
  // return size wrotten
  int i;
  const byte* p = (const byte*)t;
  for( i = 0; i < (int)sizeof( TagsList ); ++i)
  {
    EEPROM.write( nOffset+i, *p );
    ++p;
  }
  return i;
}

int TagsList_addToList( TagsList * t, const  char * buf )
{
  // return 0 if nbr max reached, 1 if ok, 2 if already in the list
  Serial.println( "TagsList_addToList - begin" );
  if( TagsList_isInList( t, buf ) != -1 )
  {
    Serial.println( "TagsList_addToList - end: already in" );    
    return 2;
  }
  if( t->nNbrTags == TAGS_NBR_MAX )
  {
    Serial.println( "TagsList_addToList - end: max tags" );
    return 0;
  }
  memcpy( &(t->aaLists[t->nNbrTags][0]), buf, TAG_LEN );
  ++(t->nNbrTags);
  Serial.println( "TagsList_addToList - end: added" );  
  return 1;
}

int TagsList_removeFromList( TagsList * t, const  char * buf )
{
  // return 0 if not in list, 1 if ok
  Serial.println( "TagsList_removeFromList - begin" );
  int nIdx = TagsList_isInList( t, buf );
  if( nIdx == -1  )
  {
    Serial.println( "TagsList_removeFromList - end - NOT FOUND" );
    return 0;
  }
  memcpy( &(t->aaLists[nIdx][0]), &(t->aaLists[nIdx+1][0]), TAG_LEN*(t->nNbrTags-nIdx-1) ); // decale tout
  --(t->nNbrTags);
  Serial.println( "TagsList_removeFromList - end - ok" );
  return 1;
}

int TagsList_isInList( const TagsList * t, const  char * buf )
{
  // return the index in the list or -1 if not in the list
  Serial.print( "TagsList_isInList - begin - list has nbr elem: " );  
  Serial.println( t->nNbrTags );
  int i;
  for( i = 0; i < t->nNbrTags; ++i )
  {
    if( memcmp( buf, &(t->aaLists[i][0]), TAG_LEN ) == 0 )
    {
      Serial.println( "TagsList_isInList - end: found" );
      return i;
    }
  }
  Serial.println( "TagsList_isInList - end: NOT found" );
  return -1;
}

int TagsList_isMagic( const char * buf )
{
  for( int i = 0; i < NBR_MAGIC_TAG_DIFFERENT; ++i )
  {
    if( memcmp( buf, &(aMagicTagList_Memorize[i][0]), TAG_LEN ) == 0 )
    {
      Serial.println( "TagsList_isMagic: Memorize!" );
      return 1;
    }
    if( memcmp( buf, &(aMagicTagList_Forget[i][0]), TAG_LEN ) == 0 )
    {
      Serial.println( "TagsList_isMagic: Forget!" );      
      return 2;
    }    
  }
  return 0;
}


const byte nEepromVersion = 1;
void load_eeprom(TagsList * pTagsList, int nNbrReader)
{
  byte nEepromCurrent = EEPROM.read( 0 );
  Serial.print( "eeprom current version: " );
  Serial.println( nEepromCurrent );
  if( nEepromVersion != nEepromCurrent )
  {
    return;
  }
  Serial.println( "Loading eeprom..." );
  int nOffset = 1;
  for( int i = 0; i < nNbrReader; ++i )
  {
    nOffset += TagsList_readFromEprom( &pTagsList[i], nOffset );
  }  
}

void save_eeprom(TagsList * pTagsList, int nNbrReader)
{
  Serial.println( "Saving eeprom..." );
  EEPROM.write( 0, nEepromVersion );
  int nOffset = 1;
  for( int i = 0; i < nNbrReader; ++i )
  {
    nOffset += TagsList_writeToEprom( &pTagsList[i], nOffset );
  }  
}

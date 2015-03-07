#include <Arduino.h> // for byte
#include <../../../../libraries/EEPROM/EEPROM.h> // => generate error when in a .c



//About eeprom:
// WRN: can't write more than 100000 times. initialised at 0xFF but can change => use a pgm version number

#include "tags.h"


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
  if( TagsList_isInList( t, buf ) )
  {
    return 2;
  }
  if( t->nNbrTags == TAGS_NBR_MAX )
  {
    return 0;
  }
  memcpy( &(t->aaLists[t->nNbrTags][0]), buf, TAG_LEN );
  ++(t->nNbrTags);
  Serial.println( "TagsList_addToList - end" );  
  return 1;
}

int TagsList_isInList( const TagsList * t, const  char * buf )
{
  // return 1 if the tag in buf is in the list
  Serial.println( "TagsList_isInList - begin" );  
  int i;
  for( i = 0; i < t->nNbrTags; ++i )
  {
    if( memcmp( buf, &(t->aaLists[i][0]), TAG_LEN ) == 0 )
    {
      Serial.println( "TagsList_isInList - end: 1" );
      return 1;
    }
  }
  Serial.println( "TagsList_isInList - end: 0" );
  return 0;
}

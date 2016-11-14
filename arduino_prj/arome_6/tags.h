
#define TAG_LEN 12         // len of one tag in byte
#define TAGS_NBR_MAX 10   // nbr max of tags in the list

typedef struct _TagsList
{
  int   nNbrTags;
  char  aaLists[TAGS_NBR_MAX][TAG_LEN];
}TagsList;

void TagsList_init( TagsList * t );

int TagsList_readFromEprom( TagsList * t, int nOffset );
int TagsList_writeToEprom( const TagsList * t, int nOffset );

int TagsList_addToList( TagsList * t, const char * buf );
int TagsList_removeFromList( TagsList * t, const char * buf );
int TagsList_isInList( const TagsList * t, const char * buf );

int TagsList_isMagic( const char * buf ); // return 0 for standard tag, 1 if tag memorize, 2 if tag forget, 3 if tag demo

// load and save all tags list from eeprom (should'nt be here but inclusion of eeprom generate a lot of error, so...)
int load_eeprom(TagsList * pTagsList, int nNbrReader); // return currentmode: bRainbowMode:1 or normal: 0
void save_eeprom(TagsList * pTagsList, int nNbrReader, int bRainbowMode);

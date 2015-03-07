
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

int TagsList_addToList( TagsList * t, const  char * buf );
int TagsList_isInList( const TagsList * t, const  char * buf );


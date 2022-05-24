#ifndef IMGS_H
#define IMGS_H
extern const unsigned char aImgs[] PROGMEM; // putting unsigned type * generate an error: aImgs is set to 0
extern const unsigned char aPalette[] PROGMEM;
#define IMG_SIZE_X 44
#define IMG_SIZE_Y 64
#define IMG_NBR_BITS 4
#define IMG_NBR    1
#endif // IMGS_H

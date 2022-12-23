// Simplest touch screen method library with X Y and Z (pressure)
// (c) ladyada / adafruit + A.Mazel / Factory
// Code under MIT License

#ifndef SIMPLE_TOUCH_DETECTION_H
#define SIMPLE_TOUCH_DETECTION_H

#define PORTRAIT  0
#define LANDSCAPE 1

int std_init();
//int std_start();
int std_getPressed(int * px, int * py, int * pz, bool bDebug = 1);

#endif // SIMPLE_TOUCH_DETECTION_H
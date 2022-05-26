// TouchScreen_Calibr_native for MCUFRIEND UNO Display Shields
// adapted by David Prentice
// for Adafruit's <TouchScreen.h> Resistive Touch Screen Library
// from Henning Karlsen's original UTouch_Calibration program.
// Many Thanks.

#define PORTRAIT  0
#define LANDSCAPE 1
#define USE_XPT2046   0
#define USE_LOCAL_KBV 1

#define TOUCH_ORIENTATION  PORTRAIT
#define TOUCH_ORIENTATION  LANDSCAPE

#if defined(USB_PID) && USB_PID == 0x804E // Arduino M0 Native
#define Serial SerialUSB
#endif

#define SWAP(x, y) { int t = x; x = y; y = t; }

#define TITLE "TouchScreen.h GFX Calibration"
#include <Adafruit_GFX.h>
#include <MCUFRIEND_kbv.h>
extern MCUFRIEND_kbv tft;

// MCUFRIEND UNO shield shares pins with the TFT.
#if defined(ESP32)
int XP = 27, YP = 4, XM = 15, YM = 14;  //most common configuration
#else
//int XP = 6, YP = A1, XM = A2, YM = 7;  //most common configuration
int XP = 7, YP = A2, XM = A1, YM = 6;  //next common configuration
//int XP=PB7,XM=PA6,YP=PA7,YM=PB6; //BLUEPILL must have Analog for YP, XM
#endif
#if USE_LOCAL_KBV
#include "TouchScreen_kbv.h"         //my hacked version
#define TouchScreen TouchScreen_kbv
#define TSPoint     TSPoint_kbv
#else
#include <TouchScreen.h>         //Adafruit Library
#endif
TouchScreen ts(XP, YP, XM, YM, 300);   //re-initialised after diagnose
TSPoint tp;                            //global point

void readResistiveTouch(void)
{
    tp = ts.getPoint();
    pinMode(YP, OUTPUT);      //restore shared pins
    pinMode(XM, OUTPUT);
    //digitalWrite(YP, HIGH);  //because TFT control pins
    //digitalWrite(XM, HIGH);
    //    Serial.println("tp.x=" + String(tp.x) + ", tp.y=" + String(tp.y) + ", tp.z =" + String(tp.z));
}

uint16_t readID(void) {
    uint16_t ID = tft.readID();
    if (ID == 0xD3D3) ID = 0x9486;
    return ID;
}
#define TFT_BEGIN()  tft.begin(ID)

#define WHITE 0xFFFF
#define RED   0xF800
#define BLUE  0x001F
#define GREEN 0x07E0
#define BLACK 0x0000

//#define GRAY  0x2408        //un-highlighted cross-hair
#define GRAY      BLUE     //idle cross-hair colour
#define GRAY_DONE RED      //finished cross-hair

int std_init()
{
    char buf[40];
    uint16_t ID = readID();
    TFT_BEGIN();
    tft.fillScreen(TFT_NAVY);
    tft.println("Waiting for Serial");
    delay(1000);
    Serial.begin(9600);
    while (!Serial);
    tft.fillScreen(TFT_BLUE);
    Serial.println(TITLE);
    bool ret = true;
#if USE_XPT2046 || defined(__arm__) || defined(ESP32)
    Serial.println(F("Not possible to diagnose Touch pins on ARM or ESP32"));
#else
    //ret = diagnose_pins();  //destroys TFT pin modes
    TFT_BEGIN();            //start again
#endif
    tft.setRotation(TOUCH_ORIENTATION);
    //dispx = tft.width();
    //dispy = tft.height();
    //text_y_center = (dispy / 2) - 6;
    sprintf(buf, "ID = 0x%04x", ID);
    Serial.println(buf);
    if (ret == false) {
        Serial.println("ERR: std_init: Something is broken ?");
    }
}

int std_getPressed(int * x, int * y, int * z)
{
  // return 1 if somethi is pressed, x,y,and z are then filled
  // fill x, y & z
  // .kbv was too sensitive !!
  // now touch has to be stable for 50ms
  // 
  int count = 0;
  bool pressed, prev_pressed=0;
  while (count < 10) {
      readResistiveTouch();
      pressed = tp.z < 1750;     //ADJUST THIS VALUE TO SUIT YOUR SCREEN e.g. 20 ... 250
      //Serial.println(tp.z);
      if( pressed == prev_pressed ) 
      {
        count++;
      }
      else 
      {
        //Serial.println("stat diff oldstate");
        count = 0;
        prev_pressed = pressed;
      }
      delay(5);
  }
  if( pressed )
  {
    *x = tp.x;
    *y = tp.y;
    *z = tp.z;
  }
  return pressed;
}
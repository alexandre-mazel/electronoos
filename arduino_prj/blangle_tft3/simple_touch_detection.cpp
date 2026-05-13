// TouchScreen_Calibr_native for MCUFRIEND UNO Display Shields
// adapted by David Prentice
// for Adafruit's <TouchScreen.h> Resistive Touch Screen Library
// from Henning Karlsen's original UTouch_Calibration program.
// Many Thanks.

#define USE_XPT2046   0
#define USE_LOCAL_KBV 1

#include "simple_touch_detection.h"

#define TOUCH_ORIENTATION  PORTRAIT
#define TOUCH_ORIENTATION  LANDSCAPE // Doit etre le meme que celui du rendu

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
//int XP = 7, YP = A2, XM = A1, YM = 6;  //next common configuration
//int XP=PB7,XM=PA6,YP=PA7,YM=PB6; //BLUEPILL must have Analog for YP, XM
//int XP = 6, YP = A2, XM = A1, YM = 7;  //my alex configuration
int XP = 8, YP = A3, XM = A2, YM = 9;  // tft2 config 0X9487

//const int XP=8,XM=A2,YP=A3,YM=9; 
//320x480 ID=0x9487 const int TS_LEFT=193,TS_RT=920,TS_TOP=962,TS_BOT=198;
//PORTRAIT CALIBRATION 320 x 480x = map(p.x, LEFT=193, RT=920, 0, 320)y = map(p.y, TOP=962, BOT=198, 0, 480)
//LANDSCAPE CALIBRATION 480 x 320 x = map(p.y, LEFT=962, RT=198, 0, 480)y = map(p.x, TOP=920, BOT=193, 0, 320)

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
  return;
  // la fonction n'amene pas grand chose
  // le seul truc interessant pourrait etre ca:
/*
  uint16_t ID = tft.readID();
  Serial.print("TFT ID = 0x");
  Serial.println(ID, HEX);
  Serial.println("Calibrate for your Touch Panel");
  if (ID == 0xD3D3) ID = 0x9486; // write-only shield
  tft.begin(ID);

  return;
*/

# if 0
  
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
#endif // 0
}

int std_getPressed(int * px, int * py, int * pz, bool bDebug )
{
  // return 1 if something is pressed, x,y,and z are then filled
  // fill x, y & z
  // .kbv was too sensitive !!
  // now touch has to be stable for 50ms
  // 
  
  static int xmin_calib = 9999;
  static int xmax_calib = 0;
  static int ymin_calib = 9999;
  static int ymax_calib = 0;

  long int xraw = 0; // compute average of touch
  long int yraw = 0;
  
  int count = 0;
  bool pressed, prev_pressed=0;
  while (count < 10) {
      readResistiveTouch();
      pressed = tp.z > 160;     // ADJUST THIS VALUE TO SUIT YOUR SCREEN e.g. 20 ... 250 // was 1750
      //Serial.println(tp.z);
      if( pressed == prev_pressed ) 
      {
        count++;
        if( pressed )
        {
          //Serial.println(tp.x);
          xraw += tp.x;
          yraw += tp.y;
        }
      }
      else 
      {
        //Serial.println("stat diff oldstate");
        count = 0;
        xraw = 0;
        yraw = 0;
        prev_pressed = pressed;
      }
      delay(1);
  }
  if( pressed )
  {
    if( bDebug )
    {
      Serial.println("PRESSED!");
    }
    xraw /= count;
    yraw /= count;

    // deja vu dans le soft:
    // 100/433 612/981
    // 115/413 684/947
    // 108/455 573/970

    // d'apres soft de calib: 125/949 et 155/936
    // autre calib: 124/954 et 143/930
    // 12/12/2022: x: 292/965 y:  136/968

    // quand on regarde l'ecran en paysage avec l'usb en haut a gauche

    // quand l'ecran est en orientation portrait
    // xraw: min en bas, max en haut
    // yraw: min a gauche, max a droite

    // quand l'ecran est en orientation paysage
    // xraw: min en bas, max en haut
    // yraw: min a gauche, max a droite

    int xmin = 187;
    int xmax = 885;
    int ymin = 172;
    int ymax = 935;
    int w = 480;
    int h = 320;
    int invert_x=0; // was 1 before rotating screen
    int invert_y=0; // was 1 before rotating screen

    int x = xraw;
    int y = yraw;

    if( 0 )
    {
        // use info from mcu_touchscreen_calib
        x = map(y, 962, 198, 0, 480);
        y = map(x, 920, 193, 0, 320);
    }
    else
    {
      // auto calibration on the fly system

      if( pressed )
      {
        if( x > xmax_calib) xmax_calib = x;
        if( x < xmin_calib) xmin_calib = x; 
        if( y > ymax_calib) ymax_calib = y;
        if( y < ymin_calib) ymin_calib = y; 
      }
      const int bUseCalibOnTheFly = 0;
      if(TOUCH_ORIENTATION==PORTRAIT)
      {
        if( !bUseCalibOnTheFly )
        {
          x = (long)((x-xmin))*h/(xmax-xmin);
          y = (long)((y-ymin))*w/(ymax-ymin);
        }
        else
        {
          // use calib on the fly
          x = (long)((x-xmin_calib))*h/(xmax_calib-xmin_calib);
          y = (long)((y-ymin_calib))*w/(ymax_calib-ymin_calib);
        }
      }
      else
      {
        // swap x <==> y
        int a = x;
        x = y;
        y = a;
        if( !bUseCalibOnTheFly )
        {
          x = (long)((x-xmin))*w/(xmax-xmin);
          y = (long)((y-ymin))*h/(ymax-ymin);
        }
        else
        {
          // use calib on the fly
          x = (long)((x-xmin_calib))*w/(xmax_calib-xmin_calib);
          y = (long)((y-ymin_calib))*h/(ymax_calib-ymin_calib);
        }
        if(invert_y) y = h-1-y;
      }

      if( invert_x ) x = w-1-x;

    } // my own calibration

    *px = x;
    *py = y;
    *pz = tp.z;

    if( bDebug && pressed)
    {
      Serial.print("touch, x: ");
      Serial.print(x);
      Serial.print(", y: ");
      Serial.print(y);
      Serial.print(", z: ");
      Serial.print(*pz);

      Serial.print(", x raw: ");
      Serial.print(xraw);
      Serial.print(", y raw: ");
      Serial.print(yraw);

      // print range:
      Serial.print(", xr: ");
      Serial.print(xmin_calib);
      Serial.print(" / ");
      Serial.print(xmax_calib);

      Serial.print(", yr: ");
      Serial.print(ymin_calib);
      Serial.print(" / ");
      Serial.print(ymax_calib);

      Serial.println();
    }
    if( 1 )
    {
      // draw a pixel on mouse click
      static int prevx = 0;
      static int prevy = 0;
      static int prevcolor = 0;
      
      //tft.drawPixel(prevx,prevy,BLACK);
      tft.drawPixel(prevx,prevy,prevcolor);
      prevcolor = tft.readPixel(x,y);
      tft.drawPixel(x,y,WHITE);
      //tft.drawPixel(x+1,y,WHITE);
      //tft.drawPixel(x,y+1,WHITE);
      //tft.drawPixel(x+1,y+1,WHITE);
      prevx = x;
      prevy = y;
    }
  }
  return pressed;
}
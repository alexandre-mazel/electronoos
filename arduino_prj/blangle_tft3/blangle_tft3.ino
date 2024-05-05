#include <EEPROM.h>
#include <Adafruit_MCP9808.h> // MCP9808 library by Adafruit

#include "Alex_LSM6DSOX.h"

/*
Le croquis utilise 31158 octets (12%) de l'espace de stockage de programmes. Le maximum est de 253952 octets.
Les variables globales utilisent 7293 octets (89%) de mémoire dynamique, ce qui laisse 899 octets pour les variables locales. Le maximum est de 8192 octets.
La mémoire disponible faible, des problèmes de stabilité pourraient survenir.

En enlevant des prints, on arrive a:
- 30944
- 7201


*/

// install tft_espi using the library manager
// or  copy TFT_eSPI-2.5.0.zip into 
// to C:\Users\alexa\Documents\Arduino\libraries

//#include <TFT_eSPI.h>
//#include <SPI.h>

//#define TFT_PARALLEL_8_BIT
//#define ILI9486_DRIVER
// try TFT_HX8357

/*
TFT_eSPI tft = TFT_eSPI();



void setup()
{
  Serial.begin(9600);
  Serial.println("setup...");
  tft.init();
  tft.setRotation(3);
  tft.fillScreen(0x0);
}

void loop()
{
  Serial.println("loop blagngle2...");
  int r;

  tft.fillScreen(0x255);
  delay(1000); 
  tft.fillScreen(0x255);
  delay(1000);

  for( r = 0; r <= 0x1f; r++ )
  {
    tft.drawLine(0,r, 639, r, (r/2) );
    tft.drawLine(0,0x20*2+r, 639, 0x20*2+r, ((r/2)<<6) ); 
  }
  
}
*/

//#include <Adafruit_GFX_Library\gfxfont.h>
#include "c:\Users\alexa\Documents\Arduino\libraries\Adafruit_GFX_Library\gfxfont.h"
#include <FreeDefaultFonts.h>
#include <FreeSevenSegNumFontPlusPlus.h>
#include <MCUFRIEND_kbv.h>
#include <TFT_PRINTGLUE.h>
#include <UTFTGLUE.h>

#include <MCUFRIEND_kbv.h>
#include "imgs.h" // cf comments in render_lock
#include "simple_touch_detection.h"

MCUFRIEND_kbv tft;

// Assign human-readable names to some common 16-bit color values:
#define BLACK   0x0000
#define BLUE    0x001F
#define RED     0xF800
#define GREEN   0x07E0
#define CYAN    0x07FF
#define MAGENTA 0xF81F
#define YELLOW  0xFFE0
#define WHITE   0xFFFF
#define GRAY    0x8410

#define PIN_PHOTORES A14
#define PIN_LOWBATTERY A15

#define PIN_SOX_I2C_CHANGE_ADDR 32


uint16_t version = MCUFRIEND_KBV_H_;

long int nCptFrame = 0;
unsigned long timeBegin = millis();
float fps = 60.;

// Create the MCP9808 temperature sensor object
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

const char sox_name1[] = "AngleRacle";
const char sox_name2[] = "AngleForNIP";

Alex_LSM6DSOX * sox1 = 0;
Alex_LSM6DSOX * sox2 = 0;

int tft_write_y = 10;
void tft_write( const char* msg )
{
  tft.setRotation(LANDSCAPE+2); // +2 => revert haut bas
  tft.setTextSize(3);
  tft.setCursor( 10, tft_write_y ); tft_write_y += 30;
  tft.print(msg);
}



///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void setup()
{
  int nNumError = 0;

  Serial.begin(57600);
  //if (!Serial) delay(5000);           //allow some time for Leonardo
    

#if 1
  //tft.begin(0x7793);
  tft.begin(0x9487); // new tft
  
#else
  // autotdetect version (prend plus de ram)
    uint16_t ID = tft.readID(); //
    Serial.println(F("Diagnose whether this controller is supported"));
    Serial.println(F("There are FAQs in extras/mcufriend_how_to.txt"));
    Serial.println(F(""));
    Serial.print(F("tft.readID() finds: ID = 0x"));
    Serial.println(ID, HEX);
    Serial.println(F(""));
	  Serial.print(F("MCUFRIEND_kbv version: "));
    Serial.print(version/100);
	  Serial.print(F("."));
    Serial.print((version / 10) % 10);
	  Serial.print(F("."));
    Serial.println(version % 10);
    Serial.println(F(""));
    if (ID == 0x0404) {
        Serial.println(F("Probably a write-only Mega2560 Shield"));
        Serial.println(F("#define USE_SPECIAL in mcufriend_shield.h"));
        Serial.println(F("#define appropriate SPECIAL in mcufriend_special.h"));
        Serial.println(F("e.g. USE_MEGA_16BIT_SHIELD"));
        Serial.println(F("e.g. USE_MEGA_8BIT_SHIELD"));
        Serial.println(F("Hint.  A Mega2560 Shield has a 18x2 male header"));
        Serial.println(F("Often a row of resistor-packs near the 18x2"));
        Serial.println(F("RP1-RP7 implies 16-bit but it might be 8-bit"));
        Serial.println(F("RP1-RP4 or RP1-RP5 can only be 8-bit"));
    }
    if (ID == 0xD3D3) {
        uint16_t guess_ID = 0x9481; // write-only shield
        Serial.println(F("Probably a write-only Mega2560 Shield"));
        Serial.print(F("Try to force ID = 0x"));
        Serial.println(guess_ID, HEX);
        tft.begin(guess_ID);
    }
    else tft.begin(ID);
    Serial.println(F(""));
    if (tft.width() == 0) {
        Serial.println(F("This ID is not supported"));
        Serial.println(F("look up ID in extras/mcufriend_how_to.txt"));
        Serial.println(F("you may need to edit MCUFRIEND_kbv.cpp"));
        Serial.println(F("to enable support for this ID"));
        Serial.println(F("e.g. #define SUPPORT_8347D"));
        Serial.println(F(""));
        Serial.println(F("New controllers appear on Ebay often"));
        Serial.println(F("If your ID is not supported"));
        Serial.println(F("run LCD_ID_readreg.ino from examples/"));
        Serial.println(F("Copy-Paste the output from the Serial Terminal"));
        Serial.println(F("to a message in Displays topic on Arduino Forum"));
        Serial.println(F("or to Issues on GitHub"));
        Serial.println(F(""));
        Serial.println(F("Note that OPEN-SMART boards have diff pinout"));
        Serial.println(F("Edit the pin defines in LCD_ID_readreg to match"));
        Serial.println(F("Edit mcufiend_shield.h for USE_SPECIAL"));
        Serial.println(F("Edit mcufiend_special.h for USE_OPENSMART_SHIELD_PINOUT"));
       while (1);    //just die
    } else {
        Serial.print(F("PORTRAIT is "));
        Serial.print(tft.width());
        Serial.print(F(" x "));
        Serial.println(tft.height());
        Serial.println(F(""));
        Serial.println(F("Run the examples/graphictest_kbv sketch"));
        Serial.println(F("All colours, text, directions, rotations, scrolls"));
        Serial.println(F("should work.  If there is a problem,  make notes on paper"));
        Serial.println(F("Post accurate description of problem to Forum"));
        Serial.println(F("Or post a link to a video (or photos)"));
        Serial.println(F(""));
        Serial.println(F("I rely on good information from remote users"));

        tft.fillScreen(BLUE);
    }

#endif
  
  //std_init();

  delay(300);

  tft.fillScreen(BLACK);
  Serial.println("");
  Serial.println("");
  Serial.println("");
  Serial.println("");

  sox1 = new Alex_LSM6DSOX(sox_name1);
  sox2 = new Alex_LSM6DSOX(sox_name2);


  if( !sox1->begin_I2C(0x6A) )
  {
    Serial.println("ERR: Can't find imu1!");
    tft_write("ERR 1: Can't find imu1!");
    ++nNumError;
  }
  else
  {
    Serial.println("INF: Found imu1!");
    sox1->setAccelDataRate(LSM6DS_RATE_104_HZ);
    sox1->printConfig();
  }

  // passe le capteur 2 sur une autre adresse
  pinMode(PIN_SOX_I2C_CHANGE_ADDR, OUTPUT);
  digitalWrite(PIN_SOX_I2C_CHANGE_ADDR ,HIGH);

  if( !sox2->begin_I2C(0x6B) )
  {
    Serial.println("ERR: Can't find imu2!");
    tft_write("ERR 2: Can't find imu2!");
    ++nNumError;
  }
  else
  {
    Serial.println("INF: Found imu2!");
    sox2->setAccelDataRate(LSM6DS_RATE_104_HZ);
    sox2->printConfig();
  }

  if (!tempsensor.begin(0x18)) 
  {
    Serial.println("ERR: Can't find temperature sensor MCP9808!");
    tft_write("WRN 1: Can't find temp sens");
    ++nNumError;
  }
  else
  {
    Serial.println("INF: Found temperature sensor MCP9808!");
    tempsensor.setResolution(1); // 0: 30ms, 1: 65 ms
  }

  pinMode( PIN_PHOTORES, INPUT );
  pinMode( PIN_LOWBATTERY, INPUT );
  

  Serial.println("INF: Blangle v0.8");  
  Serial.println("INF: Starting...");
  if( nNumError == 0 )
  {
    Serial.println("INF: Everything looks GOOD !");
  }
  else
  {
    Serial.print("INF: error(s) detected nbr: ");
    Serial.println(nNumError);
    delay(3000);
  }

  loadConfigFromEeprom();

} // setup





int render_img( const int x, const int y, const int w, const int h, const unsigned char* pImg, const unsigned char* pPalette, int flip=0, int neg=0)
{
  // flip: 0: none, 1: flip vertical

  const int bDebug = 0;

  for(int j = 0; j < h; ++j)
  {
    for(int i = 0; i < w; ++i)
    {
      // mode 4 bits per pixel in palette
      int idx = pImg[(i/2)+(j*w/2)];

      if( bDebug )
      {
        Serial.print("i: ");
        Serial.println(i);
        Serial.print("idx avant:");
        Serial.println(idx);
      }

      idx = (idx>>(4*(i%2)))&0x0F;

      if( bDebug )
      {
        Serial.print("idx apres:");
        Serial.println(idx);
      }

      uint16_t b = (uint16_t)pPalette[idx*3+0];
      uint16_t g = (uint16_t)pPalette[idx*3+1];
      uint16_t r = (uint16_t)pPalette[idx*3+2];

      if( bDebug )
      {
        Serial.print("r: 0x");
        Serial.print(r,HEX);
        Serial.print(", g: 0x");
        Serial.print(g,HEX);
        Serial.print(", b: 0x");
        Serial.println(b,HEX);
      }

      // pixel format: 565

      uint16_t color = (uint16_t)( ((r>>3)<<11 ) | ((g>>2)<<5 ) | ((b>>3)) );

      if( bDebug )
      {
        Serial.print("color: 0x");
        Serial.println(color,HEX);
      }

      if( (color != 0 && !neg) || (neg && color == 0))
      {
        //color = 0xF800;
        if( flip == 0 )
          tft.drawPixel((int16_t)(x+i),(int16_t)(y+j),(uint16_t)color);
        else
          tft.drawPixel((int16_t)(x+i),(int16_t)((y+w-1-j)),(uint16_t)color);
      }
      
      if( bDebug )
      {
        Serial.print("color: 0x"); 
        Serial.println(color, HEX);
      }
    }
  }  
}

int render_lock(int x,int y)
{
  // sur Uno quand l'image etait trop grosse il ne restait que 148 octets pour les variables locales et ca faisait nimp

  // generated from electronoos\generate_img.py:
  // python C:\Users\alexa\dev\git\electronoos\generate_img\generate_img.py "C:\Users\alexa\perso\docs\2022-05-20_-_blangle_tft\just_lock.png" "C:\Users\alexa\perso\docs\2022-05-20_-_blangle_tft\just_arrow.png" "C:\Users\alexa\perso\docs\2022-05-20_-_blangle_tft\bubble.png" 4
  // snas la bubble
  // python C:\Users\alexa\dev\git\electronoos\generate_img\generate_img.py "C:\Users\alexa\perso\docs\2022-05-20_-_blangle_tft\just_lock.png" "C:\Users\alexa\perso\docs\2022-05-20_-_blangle_tft\just_arrow.png" 4
  // copy \tmp\imgs.* C:\Users\alexa\dev\git\electronoos\arduino_prj\blangle_tft2\ /Y

  render_img(x,y,IMG_1_SIZE_X,IMG_1_SIZE_Y,aImgs_1,aPalette_1);
}

int render_arrow(int x,int y,int flip=0)
{
  render_img(x,y,IMG_2_SIZE_X,IMG_2_SIZE_Y,aImgs_2,aPalette_2,flip);
}

int render_bubble(int x,int y)
{
  //render_img(x,y,IMG_3_SIZE_X,IMG_3_SIZE_Y,aImgs_3,aPalette_3,0,1); // trait noir
  //render_img(x,y,IMG_3_SIZE_X,IMG_3_SIZE_Y,aImgs_3,aPalette_3,0,0); // trait blanc (palette changé a la main dans le fichier généré)
}


float readFloatFromEeprom( int nOffset )
{
  float val;
  byte *p = (byte*)&val;
  for( int i = 0; i < sizeof(float); ++i)
  {
      (*p) = EEPROM.read(nOffset);
      ++nOffset;
      ++p;
  }
  //Serial.print( "readFloatFromEeprom: " );
  //Serial.println( val );
  return val;
}

double readDoubleFromEeprom( int nOffset )
{
  //Serial.print( "nOffset: " );
  //Serial.println( nOffset );
  float val;
  byte *p = (byte*)&val;
  for( int i = 0; i < sizeof(double); ++i)
  {
      (*p) = EEPROM.read(nOffset);
      ++nOffset;
      ++p;
  }
  //Serial.print( "readDoubleFromEeprom: " );
  //Serial.println( val );
  return val;
}

void writeFloatToEeprom( int nOffset, float val )
{
  //Serial.print("sizeof float: ");
  //Serial.println(sizeof(float));

  const byte *p = (byte*)&val;
  for( int i = 0; i < sizeof(float); ++i)
  {
      EEPROM.write(nOffset,*p);
      ++nOffset;
      ++p;
  }
}

void writeDoubleToEeprom( int nOffset, double val )
{
  //Serial.print( "writeDoubleToEeprom: " );
  //Serial.println( val );
  //Serial.print( "nOffset: " );
  //Serial.println( nOffset );

  //Serial.print("sizeof double: "); // on Mega2560, float=double=32bits
  //Serial.println(sizeof(double));

  const byte *p = (byte*)&val;
  for( int i = 0; i < sizeof(double); ++i)
  {
      EEPROM.write(nOffset,*p);
      ++nOffset;
      ++p;
  }
}


const int nNbrSettings = 8;
int nNumSettingsSelected = 0; // 0 to nNbrSettings-1


double presetCirc[nNbrSettings] = {628.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0}; // en mm

const byte nEepromVersion = 100; // to differentiate from other program (arome...)
void loadConfigFromEeprom()
{
  int nOffset = 0;
  byte nEepromCurrent = EEPROM.read( nOffset );  nOffset += 1;
  Serial.print( "eeprom current version: " );
  Serial.println( nEepromCurrent );
  if( nEepromVersion != nEepromCurrent )
  {
      // eg: first read
      return;
  }
  Serial.println( "Loading eeprom..." );
  
  nNumSettingsSelected = EEPROM.read( nOffset );  nOffset += 1;
  //Serial.print( "nNumSettingsSelected: " );
  //Serial.println( nNumSettingsSelected );
  
  for( int i = 0; i < nNbrSettings; ++i)
  {
      presetCirc[i] = readDoubleFromEeprom( nOffset ); nOffset += sizeof(double);
  }
}

void saveConfigToEeprom()
{
  int nOffset = 0;
  Serial.println("INF: saveConfigToEeprom");
  EEPROM.write( nOffset, nEepromVersion ); nOffset += 1;
  EEPROM.write( nOffset, nNumSettingsSelected ); nOffset += 1;
  for( int i = 0; i < nNbrSettings; ++i)
  {
      writeDoubleToEeprom( nOffset,presetCirc[i] ); nOffset += sizeof(double);
  }
}


const int w_screen = 480; // 400
const int h_screen = 320; // 240
const int nMenuW = 36;
const int nMenuH = h_screen;

const int nBubbleW = 0; // bubble level (was 32 to render it)
const int nBubbleH = h_screen;
const int nAreaW = (w_screen-nMenuW-nBubbleW)/2; // width of an area
const int nAreaH = h_screen/2;
const int nLineH = 8;

const int xLock = nMenuW+342;
const int yLock = nAreaH+20;

const int wLock = 88;
const int hLock = 124;

const int xArrow = nMenuW+88;
const int yArrow = nAreaH+32;
const int yArrowBottom = nAreaH+80+30;
const int wArrow = 20;
const int wInterArrow = 10;

int render_screen(int nPresel, int nip, int db, int bubble, double circ,int bLocked, float rTemperature, int nLuminosity, bool bLowBattery)
{
  static uint8_t bDrawed = 0;
  static uint8_t bPrevLocked = 2;
  static int nPrevPresel = -1;
  static int nPrevDb = 9999;
  static int nPrevNip = 9999;
  static int nPrevBubble = 9999;
  char buf[8];
  
  // dessine l'interface, ne redessinne que ce qui est utile

  const int w = w_screen;
  const int h = h_screen;



  int nBubblePos = 0;

  if( 0 )
  {
    if( ! bDrawed )
    {
      bDrawed = 1;
      // just gray
      tft.fillRect(0,0,640,640,GRAY);
    }
    return 0;
  }

  if( ! bDrawed )
  {
    bDrawed = 1;
    tft.setRotation(LANDSCAPE+2); // +2 => revert haut bas
    //tft.fillScreen(BLACK);
    tft.setTextColor(WHITE);
    tft.fillRect(0,0,nMenuW,nMenuH,GRAY);
    tft.fillRect(nMenuW,0,nAreaW,nAreaH,BLUE);
    tft.fillRect(nMenuW+nAreaW,0,nAreaW,nAreaH,RED);
    tft.fillRect(nMenuW,nAreaH,nAreaW*2,nAreaH,BLACK);
  }

  if( nPrevPresel != nPresel)
  {
    nPrevPresel = nPresel;
    for( int i = 0; i < nNbrSettings; ++i)
    {
      if( i == nPresel )
      {
       tft.setTextColor(BLUE); 
      }
      else
      {
        tft.setTextColor(WHITE);
      }
      tft.setCursor(10, 6+i*h/nNbrSettings);
      tft.setTextSize(3);
      tft.print(i+1);
    }
    tft.setTextColor(WHITE);
  }


  tft.setTextSize(5);
  const int yText = 40;

  if(nPrevNip != nip || !bDrawed )
  {
    nPrevNip = nip;
    tft.fillRect(nMenuW,0+nAreaH/2,nAreaW,nAreaH/2,BLUE);
    tft.setCursor(nMenuW+50, yText);
    tft.print("NIP");
    tft.setCursor(nMenuW+50, yText+nLineH*5);
    
    if(nip>999)
    {
      tft.print("???");
    }
    else
    {
      tft.print(nip);
      tft.print("mm");
    }
  }

  if(nPrevDb != db )
  {
    nPrevDb = db;
    tft.fillRect(nMenuW+nAreaW,0+nAreaH/2,nAreaW,nAreaH/2,RED);
    tft.setCursor(nMenuW+nAreaW+50, yText);
    tft.print("DB");
    tft.setCursor(nMenuW+nAreaW+50, yText+nLineH*5);
    if(db>360)
    {
      tft.print("???");
    }
    else
    {
      tft.print(db/10.,1);
      tft.setCursor(tft.getCursorX(), yText+nLineH*5-nLineH+2);
      tft.setTextSize(3);
      tft.print("o");
    }
  }

  tft.setTextSize(5);
  tft.setCursor(nMenuW+20, nAreaH+64);
  tft.print("C=");
  tft.setCursor(tft.getCursorX()+8, tft.getCursorY()); // half space
  tft.setTextColor(WHITE, BLACK);
  //tft.print(circ,1);

  snprintf(buf,8,"%4d.%1d", int(circ),int( 0.5+(circ-int(circ))*10 ) );
  tft.print(buf);
  tft.setTextColor(WHITE);
  tft.print("mm");

  if(nPrevBubble != bubble && 0 )
  {
    // render bubble
    const int nBubbleSize2=32/2;
    nPrevBubble = bubble;
    int bubble_back_color = GREEN;
    if(bubble>5 || bubble<-5) bubble_back_color = MAGENTA; // half degree => bad
    tft.fillRect(w-nBubbleW,0,w,h,bubble_back_color);
    nBubblePos = (bubble/10.)*(bubble/10.);
    if(nBubblePos>h/2-nBubbleSize2) nBubblePos = h/2-nBubbleSize2;
  //  if(nBubblePos<-(h/2-nBubbleSize2)) nBubblePos = -(h/2-nBubbleSize2);
    if(bubble>0) nBubblePos=h/2-16-nBubblePos;
    else nBubblePos=h/2-16+nBubblePos;
    render_bubble(w-nBubbleW+2,nBubblePos);
    tft.drawRect(w-nBubbleW,h/2-nBubbleSize2-2,nBubbleW,2,BLACK);
    tft.drawRect(w-nBubbleW,h/2+nBubbleSize2,nBubbleW,2,BLACK);
  }
  


  if( bPrevLocked != bLocked )
  {
    bPrevLocked = bLocked;
    render_lock(xLock, yLock);

    int x = xArrow;
    if( ! bLocked )
    {
      // cache le haut du verrou
      tft.fillRect(xLock, yLock,80,48,BLACK);

      // affiche les fleches
      
      for( int i = 0; i < 5; ++i )
      {
        if( i == 4 ) x += wArrow+wInterArrow;
        render_arrow(x,yArrow);
        render_arrow(x,yArrowBottom, 1);
        x += wArrow+wInterArrow;
      }
    }
    else
    {
      // cache les fleches
      tft.fillRect( xArrow, yArrow,144+32,16,BLACK );
      tft.fillRect( xArrow, yArrowBottom+8,144+32,16,BLACK );
    }
  }

  if(1)
  {
    
    const int nOffsetY = -20;


    tft.setTextSize(2);
    tft.fillRect( nMenuW+50+46, yText+nOffsetY,48, 16, BLUE );
    tft.setCursor( nMenuW+50, yText+nOffsetY );
    tft.print("temp:");
    if(isnan(rTemperature))
    {
      tft.print("???");
    }
    else
    {
      tft.print(rTemperature, 2);
    }
    tft.print("  ");

    tft.fillRect( nMenuW+nAreaW+50+46, yText+nOffsetY,48, 16, RED );
    tft.setCursor( nMenuW+nAreaW+50, yText+nOffsetY );
    tft.print("lum:");
    tft.print(nLuminosity);
    tft.print(" lb:");
    tft.print(bLowBattery);
    tft.print("     ");
    
  }

  return 0;

}

unsigned long fpsTimeStart = 0;
unsigned long fpsCpt = 0;
void countFps()
{
  fpsCpt += 1;

  // optim: don't read millis at everycall
  // gain 1.1micros per call (averaged)
  // an empty loop takes 67.15micros on mega2560 (just this function)

  if((fpsCpt&7)!=7)
  {
    return;
  }  

  unsigned long diff = millis() - fpsTimeStart;
  if (diff > 5000)
  {
    //unsigned long timeprintbegin = micros();
    float fps = (float)(fpsCpt*1000)/diff;
    Serial.print("INF: fps: ");
    Serial.print(fps);
    Serial.print(", dt: ");
  #if 1
    {
      Serial.print(1000.f/fps,3);
      Serial.println("ms");
    }
#else
    {
      Serial.print(1000000.f/fps);
      Serial.println("micros");
    }
#endif

    fpsTimeStart = millis();
    fpsCpt = 0;
    //unsigned long durationprint = micros()-timeprintbegin;
    //DEBUG.print("duration fps micros: "); // 1228micros at 57600baud !!!, 1280 at 115200 (change nothing, it's more the time to compute)
    //DEBUG.println(durationprint);
  }

} // countFps

float rTemperature = -1.f;

void loop()
{
    static uint8_t aspect = 0;
    static int nLocked = 1;
    static int nMustSave = 0;
    //static double arCirc[8] = {5550.5}; // mm
    //static double rCirc = 628.3; // proto de Vincent
    int y = 0;
    int dy = 0;
    int nip; //cm
    int db;
    int angle_db;
    int angle_nip;
    int bubble=0;
    //const int nHalfBoitierMM = 43; // demi largeur du capteur - (distance des 2 extremites de contacts)
    const int nHalfBoitierMM = 20; // taille du boitier satelitte: distance des 2 extremites de contacts / 2
    const int nLuminoLimit = 300; // to detect opening of the box


    //Serial.println("loop... blangle2");


    // update sensors

    int photores = analogRead(PIN_PHOTORES);
    int bLowBattery = analogRead(PIN_LOWBATTERY) < 512;

    if( nCptFrame%100==0 )
    {
      tempsensor.wake();   // wake up, ready to read!
      rTemperature = tempsensor.readTempC();
      tempsensor.shutdown_wake(1);
    }

    
    //bubble = bjy_getAngle(0);
    // db = bjy_getAngle(1);
    //angle_db = bjy_getAngle(1);
    //angle_nip = bjy_getAngle(0);


    //Serial.println("avant update");
    sox1->update();
    sox2->update();
    //Serial.println("apres update");

    bool bErrorNip = false;
    bool bErrorDb = false;

    float angle_db_read = sox1->getDegY();
    float angle_nip_read = sox2->getDegY();
    
    if(angle_db_read > 600.f )
    {
      bErrorDb = true;
    }

    if(angle_nip_read > 600.f )
    {
      bErrorNip = true;
    }

    angle_db = angle_db_read*10;

    //angle_nip = 900-(angle_nip_read*10);
    angle_nip = angle_nip_read*10; // remise a plat des capteurs

    if( nCptFrame%20==0 )
    {
      Serial.print("angle_db: "); Serial.print(angle_db); Serial.print(", angle_nip: "); Serial.println(angle_nip);
      sox1->printValues();
      sox2->printValues();
    }

        //angle_db = bjy_getAngle(1);
    //angle_nip = bjy_getAngle(0);


    angle_nip -= 6; // calibration en hard (lecture du zero quand posé a plat) todo stocke dans eeprom
    angle_db -= 7; // sur la tranche on doit avoir 90, calibration en hard todo: => eeprom
    //angle_db -= 900; // offset face=>tranche - pas la peine, car on veut la difference par rapport a la verticale et pas l'horizontale
    //nip = 2*rCirc*3.14159265358979323846264*db/360;
    nip = (presetCirc[nNumSettingsSelected]*angle_nip/360)/10/1; // /10 for angle, then /10 for cm or /1 for mm

    nip += nHalfBoitierMM;
    //nip -= 21; // calib en reel;


    // db = angle_db; // pour afficher le capteur brut apres calib
    db = angle_db - ( angle_nip + 3600*(nHalfBoitierMM / presetCirc[nNumSettingsSelected]));
    // db = (900-angle_db) - ( angle_nip + 3600*(nHalfBoitierMM / presetCirc[nNumSettingsSelected]));
    

    //db = analogRead(A15)*(5.0*8 / 1023.0);

    if(bErrorNip)
    {
      nip = 6666;
    }
    if(bErrorNip || bErrorDb)
    {
      db = 6666;
    }

    

    if(0)
    { // code de test/debug
      const char *aspectname[] = 
      {
          "PORTRAIT test1", "LANDSCAPE", "PORTRAIT_REV", "LANDSCAPE_REV"
      };
      const char *colorname[] = { "BLUE", "GREEN", "RED", "GRAY" };
      uint16_t colormask[] = { BLUE, GREEN, RED, GRAY };
      if( 0 )
      {
        uint16_t ID = tft.readID(); //
        tft.setRotation(aspect);
        int width = tft.width();
        int height = tft.height();
        tft.fillScreen(colormask[aspect]);
        tft.drawRect(0, 0, width, height, WHITE);
        tft.drawRect(32, 32, width - 64, height - 64, WHITE);
        tft.setTextSize(2);
        tft.setTextColor(BLACK);
        tft.setCursor(40, 40);
        tft.print("ID=0x");
        tft.print(ID, HEX);
        if (ID == 0xD3D3) tft.print(" w/o");
        tft.setCursor(40, 70);
        tft.print(aspectname[aspect]);
        tft.setCursor(40, 100);
        tft.print(width);
        tft.print(" x ");
        tft.print(height);
        tft.setTextColor(WHITE);
        tft.setCursor(40, 130);
        tft.print(colorname[aspect]);
        tft.setCursor(40, 160);
        tft.setTextSize(1);
        tft.print("MCUFRIEND_KBV_H_ test alex= ");
        tft.print(version);

        tft.setCursor(40, 180);
        tft.print("coucou petit");
        tft.setCursor(0, 200);
        tft.setTextSize(5);
        tft.print("coucou grand");
        if (++aspect > 3) aspect = 0;
        delay(3000);
      }
      else
      {
        tft.setTextColor(WHITE, BLACK); // instead of erasing all screen, just write with black background
      }

      y = 300;
      tft.setCursor(0, y);
      tft.setTextSize(2); // 16 pixels de haut
      dy = 16;

      tft.print(int(fps)); y += dy;
      if( 0 )
      {
        tft.print("\n");
        //tft.setCursor(0, y);
        tft.print(12.3); y += dy;
        tft.print("\n"); 
        //tft.setCursor(0, y);
        tft.print(34.5); y += dy;
        tft.print("\n");
        //tft.setCursor(0, y);
        tft.print(67.8); y += dy;
      }

      delay(1);
    } // code de debug
    
    if( (nCptFrame % 2)==0 ) // reading every frame prevent serial reading ?!?
    {
      // detect touch - center of the point
      int x,y,z;
      bool bPressed = std_getPressed(&x,&y,&z,false);
      if( bPressed )
      {
        const int dw_arrow = wArrow+wInterArrow;
        const int dh_arrow = 58;
        short int listPos[(1+5*2)*2+8*2] = {
                    xLock+wLock/2,yLock+hLock/2, // lock // 370/200 // 360/182
                    // 80,120, // first arrow
        };
        // add 10 arrows
        for( int i = 0; i < 5; ++i )
        {
          listPos[2+i*2+0] = xArrow+i*dw_arrow+wArrow/2+1;
          listPos[2+i*2+1] = yArrow+8;

          if( i == 4)
          {
            // apres la virgule
            listPos[2+i*2+0] += dw_arrow;
          }

          // fleches du bas
          listPos[2+(i+5)*2+0] = listPos[2+(i+0)*2+0];
          listPos[2+(i+5)*2+1] = listPos[2+(i+0)*2+1] + 86;

        }

        // add preselection menu
        for( int i = 0; i < 8; ++i )
        {
          listPos[22+i*2+0] = nMenuW/2;
          listPos[22+i*2+1] = (nMenuH/8)*i+16;
        }

        // debug: render touch point
        if(0)
        {
          for( int i = 0; i < sizeof(listPos)/2/2; ++i ) // /2(short) /2(x & y)
          {
            for( int j =-2; j < 3; ++j )
            {
              tft.drawPixel(listPos[2+i*2+0]+j,listPos[2+i*2+1],GREEN);
              tft.drawPixel(listPos[2+i*2+0]+j,listPos[2+i*2+1]+1,GREEN);
            }
          }
        }

        int nDistMin = 9999;
        int idx_element = -1;
        for( int i = 0; i < 11+8; ++i )
        {
          // search hit, and choose nearest if many hits (enable overlap of area (when margin bigger than object))
          int posx = listPos[i*2];
          int posy = listPos[i*2+1];
          int nMargin = 60;
          if(     posx - nMargin < x && posx + nMargin > x 
              &&  posy - nMargin < y && posy + nMargin > y
          )
          {
            int nDist = abs(x-posx) + abs(y-posy);
            if( nDist < nDistMin )
            {
              nDistMin = nDist;
              idx_element = i;
            }
          }
        }
        if( idx_element != -1 )
        {
          int i = idx_element;
          Serial.print("hit: ");
          Serial.println(idx_element);
          if( i == 0 )
          {
            Serial.println("press lock !");
            nLocked = ! nLocked;
            if(nLocked && nMustSave)
            {
              nMustSave = 0;
              saveConfigToEeprom();
            }
          }
          else if( i < 11 )
          {
            // arrow
            if( !nLocked)
            {
              double rAdd;
              // i = 1 to 5 pour fleches basses et 6 to 10 for low
              Serial.print("press arrow i: ");
              Serial.println(i);
              if( i < 6 )
              {
                //nAdd = pow(10,4-i)+0.5; // i = 1 => +1000 (pow 3), i = 4 => +1 (pow 0) - probleme d'arrondi, pow(10,4) => 999 !
                rAdd = pow(10,4-i)+0.01;
              }
              else
              {
                rAdd = -pow(10,4-(i-5))-0.01;
              }
              Serial.print("rAdd: ");
              Serial.println(rAdd,6);
              presetCirc[nNumSettingsSelected] += rAdd;
              nMustSave = 1;

              // kill after centile
              presetCirc[nNumSettingsSelected] = long(0.5+presetCirc[nNumSettingsSelected]*10)/10.;

              if( presetCirc[nNumSettingsSelected] < 0 )
                presetCirc[nNumSettingsSelected] = 0;
              if( presetCirc[nNumSettingsSelected] > 9999.9 )
                presetCirc[nNumSettingsSelected] = 9999.9;

              Serial.print("new circ: ");
              Serial.println(presetCirc[nNumSettingsSelected],6);
            }
          }
          else
          {
            // presel
            nNumSettingsSelected = i-11;
          }
        } // if idx_element != -1
        
      } // if bPressed

      render_screen(nNumSettingsSelected,nip,db,bubble,presetCirc[nNumSettingsSelected],nLocked,rTemperature,photores,bLowBattery);

    } // detect touch

    //delay(40); // leave some time to system (limit to 25fps)

    //delay(1); // ! L'appel a delay nique la lecture du capteur !?!
    ++nCptFrame;
    if( nCptFrame > 40) // 400
    {
      // sur uno, avec loop delay 1 => 44fps, 43 avec un println
      // avec text size 1 => 103fps // 188 si affichÃ© en int
      // avec text size 2 => 44fps // 71/103 si afficher en int
      // avec text size 4 => 35fps
      // avec text size 6 => 27fps
      // avec text size 8 => 20fps // 49 si afficher en int (2 chars au lieu de 5)
      //
      // 1 int et 3 float sur 5 chars => 13.34fps (avec des "\n" entre apres les nbr)
      // 13.35 en mettant 4 setCursor au lieu de \n
      fps = nCptFrame*1000. / (millis()-timeBegin);
      nCptFrame = 0;
      timeBegin = millis();
      Serial.print("fps: ");
      Serial.println(fps);
      //bjy_displayLastAngles();
      Serial.print("Temperature (C): "); Serial.println(rTemperature, 1);
      Serial.print("Luminosity: "); Serial.println(photores); // ouvert, lumiere du salon de nuit: 664, ombre de la main, 111, led de tel collé dessus: 905
      Serial.print("LowBattery: "); Serial.println(bLowBattery); // ouvert, lumiere du salon de nuit: 664, ombre de la main, 111, led de tel collé dessus: 905
      
    }

    countFps();
    delay(100); // time for sensors to update
}

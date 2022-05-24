//#include <Adafruit_GFX_Library\gfxfont.h>
#include "c:\Users\alexa\Documents\Arduino\libraries\Adafruit_GFX_Library\gfxfont.h"
#include <FreeDefaultFonts.h>
#include <FreeSevenSegNumFontPlusPlus.h>
#include <MCUFRIEND_kbv.h>
#include <TFT_PRINTGLUE.h>
#include <UTFTGLUE.h>

#include <MCUFRIEND_kbv.h>
#include "imgs.h"
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

uint16_t version = MCUFRIEND_KBV_H_;

long int nCptFrame = 0;
unsigned long timeBegin = millis();
float fps = 60.;
void setup()
{
    Serial.begin(9600);
    if (!Serial) delay(5000);           //allow some time for Leonardo
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
}

int render_lock(int x,int y)
{
  // generated from electronoos\generate_img.py:
  // python C:\Users\alexa\dev\git\electronoos\generate_img\generate_img.py "C:\Users\alexa\perso\docs\2022-05-20_-_blangle_tft\just_lock.png" 4
  // copy \tmp\imgs.* C:\Users\alexa\dev\git\electronoos\arduino_prj\test_tft\ /Y
  for(int j = 0; j < IMG_SIZE_Y; ++j)
  {
    for(int i = 0; i < IMG_SIZE_X; ++i)
    {
      // mode 4 bits
      int idx = aImgs[(i/2)+j*IMG_SIZE_X];
      idx = idx>>(4*(i%2));
      int r = aPalette[idx];
      int g = aPalette[idx];
      int b = aPalette[idx];
      unsigned int color = ((r>>3)<<10 ) | ((g>>3)<<5 ) | ((b>>3));
      tft.drawPixel(x+i,y+j,aPalette[idx]);
    }
  }
}

int render_screen(int nip, int db, float circ,int bLocked)
{
  static uint8_t bDrawed = 0;
  
  // dessine l'interface, ne redessinne que ce qui est utile
  // la vraie interface 400x240
  // barre a gauche de 36 de large puis 2 zones de 182, hauteur 120
  const int w = 400;
  const int h = 240;
  const int nMenuW = 36;
  const int nMenuH = 240;
  const int nAreaW = 182;
  const int nAreaH = 120;
  const int nNbrSettings = 8;
  const int nLineH = 8;

  if( ! bDrawed )
  {
    tft.setRotation(1);
    //tft.fillScreen(BLACK);
    tft.fillRect(0,0,nMenuW,nMenuH,GRAY);
    tft.fillRect(nMenuW,0,nAreaW,nAreaH,BLUE);
    tft.fillRect(nMenuW+nAreaW,0,nAreaW,nAreaH,RED);
    tft.fillRect(nMenuW,nAreaH,nAreaW*2,nAreaH,BLACK);
    bDrawed = 1;
  }
  for( int i = 0; i < nNbrSettings; ++i)
  {
    tft.setCursor(10, 8+i*h/nNbrSettings);
    tft.setTextSize(3);
    tft.print(i+1);
  }

  tft.setTextSize(5);
  tft.setCursor(nMenuW+50, 26);
  tft.print("NIP");
  tft.setCursor(nMenuW+50, 26+nLineH*5);
  tft.print(nip);
  tft.print("cm");

  tft.setCursor(nMenuW+nAreaW+50, 26);
  tft.print("DB");
  tft.setCursor(nMenuW+nAreaW+50, 26+nLineH*5);
  tft.print(db);
  tft.setCursor(tft.getCursorX(), 26+nLineH*5-nLineH+2);
  tft.setTextSize(3);
  tft.print("o");

  tft.setTextSize(4);
  tft.setCursor(nMenuW+20, nAreaH+48);
  tft.print("C=");
  tft.setCursor(tft.getCursorX()+8, tft.getCursorY()); // half space
  tft.print(circ,1);
  tft.print("mm");

  render_lock(nMenuW+300, nAreaH+26);

}

void loop()
{
    static uint8_t aspect = 0;
    int y = 0;
    int dy = 0;
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
      if( 1 )
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
    
    if( 1 )
    {
      render_screen(20,23,5550.5,0);
    }

    ++nCptFrame;
    if( nCptFrame > 400)
    {
      // sur uno, avec loop delay 1 => 44fps, 43 avec un println
      // avec text size 1 => 103fps // 188 si affiché en int
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
      Serial.println(fps);
    }
}

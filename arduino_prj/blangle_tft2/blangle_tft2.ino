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
#include "bjy61.h"

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
  
  std_init();
  bjy_init();
}

int render_img( const int x, const int y, const int w, const int h, const unsigned char* pImg, const unsigned char* pPalette, int flip=0)
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

      if( color != 0 )
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
  // python C:\Users\alexa\dev\git\electronoos\generate_img\generate_img.py "C:\Users\alexa\perso\docs\2022-05-20_-_blangle_tft\just_lock.png" "C:\Users\alexa\perso\docs\2022-05-20_-_blangle_tft\just_arrow.png" 4
  // copy \tmp\imgs.* C:\Users\alexa\dev\git\electronoos\arduino_prj\blangle_tft2\ /Y

  render_img(x,y,IMG_1_SIZE_X,IMG_1_SIZE_Y,aImgs_1,aPalette_1);
}

int render_arrow(int x,int y,int flip=0)
{
  render_img(x,y,IMG_2_SIZE_X,IMG_2_SIZE_Y,aImgs_2,aPalette_2,flip);
}

int render_screen(int nip, int db, float circ,int bLocked)
{
  static uint8_t bDrawed = 0;
  static uint8_t bPrevLocked = 2;
  
  // dessine l'interface, ne redessinne que ce qui est utile
  // la vraie interface 400x240
  // barre a gauche de 36 de large puis 2 zones de 182, hauteur 120
  const int w = 480; // 400
  const int h = 320; // 240

  const int nMenuW = 36;
  const int nMenuH = 240;
  const int nAreaW = 182;
  const int nAreaH = 120;
  const int nNbrSettings = 8;
  const int nLineH = 8;

  if( 0 )
  {
    if( ! bDrawed )
    {
      bDrawed = 1;
      // just gray
      tft.fillRect(0,0,640,640,GRAY);
    }
    return;
  }

  if( ! bDrawed )
  {
    bDrawed = 1;
    tft.setRotation(LANDSCAPE);
    //tft.fillScreen(BLACK);
    tft.setTextColor(WHITE);
    tft.fillRect(0,0,nMenuW,nMenuH,GRAY);
    tft.fillRect(nMenuW,0,nAreaW,nAreaH,BLUE);
    tft.fillRect(nMenuW+nAreaW,0,nAreaW,nAreaH,RED);
    tft.fillRect(nMenuW,nAreaH,nAreaW*2,nAreaH,BLACK);

    for( int i = 0; i < nNbrSettings; ++i)
    {
      tft.setCursor(10, 6+i*h/nNbrSettings);
      tft.setTextSize(3);
      tft.print(i+1);
    }
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
  tft.setCursor(nMenuW+22, nAreaH+48);
  tft.print("C=");
  tft.setCursor(tft.getCursorX()+8, tft.getCursorY()); // half space
  tft.setTextColor(WHITE, BLACK);
  tft.print(circ,1);
  tft.setTextColor(WHITE);
  tft.print("mm");


  if( bPrevLocked != bLocked )
  {
    bPrevLocked = bLocked;
    render_lock(nMenuW+304, nAreaH+32);
    const int xArrow = nMenuW+75;
    const int yArrow = nAreaH+22;
    const int yArrowBottom = nAreaH+80+3;
    int x = xArrow;
    if( ! bLocked )
    {
      // cache le haut du verrou
      tft.fillRect(nMenuW+304, nAreaH+32,40,30,BLACK);

      // affiche les fleches
      
      for( int i = 0; i < 5; ++i )
      {
        if( i == 4 ) x += 24;
        render_arrow(x,yArrow);
        render_arrow(x,yArrowBottom, 1);
        x += 24;
      }
    }
    else
    {
      // cache les fleches
      tft.fillRect( xArrow, yArrow,144,16,BLACK );
      tft.fillRect( xArrow, yArrowBottom+8,144,16,BLACK );
    }
  }

}

void loop()
{
    static uint8_t aspect = 0;
    static int nLocked = 1;
    static float rCirc = 5550.5;
    int y = 0;
    int dy = 0;
    //Serial.println("loop... blangle2");

    // update sensors
    bjy_update();
    return;

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
      int x,y,z;
      bool bPressed = std_getPressed(&x,&y,&z);
      if( bPressed )
      {
        const int dw_arrow = 24;
        const int dh_arrow = 58;
        short int listPos[(1+5*2)*2] = {
                    360,182, // lock // 370/200
                    // 80,120, // first arrow
        };
        // add 10 arrows
        for( int i = 0; i < 5; ++i )
        {
          listPos[2+i*2+0] = 118+i*dw_arrow;
          listPos[2+i*2+1] = 145;//+i*dh_arrow;

          // fleches du bas
          listPos[2+(i+5)*2+0] = listPos[2+(i+0)*2+0];
          listPos[2+(i+5)*2+1] = listPos[2+(i+0)*2+1] + 61;
        }

        int nDistMin = 999999;
        int idx_element = -1;
        for( int i = 0; i < 11; ++i )
        {
          // search hit, and choose nearest if many hits (enable overlap of area (when margin bigger than object))
          int posx = listPos[i*2];
          int posy = listPos[i*2+1];
          int nMargin = 30;
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
          if( i == 0 && nLocked )
          {
            break; // don't test if locked!
          }
        }
        if( idx_element != -1 )
        {
          int i = idx_element;
          //Serial.print("hit: ");
          //Serial.println(idx_element);
          if( i == 0 )
          {
            nLocked = ! nLocked;
          }
          else
          {
            int nAdd;
            // i = 1 to 5 pour fleches basses et 6 to 10 for low
            if( i < 6 )
            {
              nAdd = pow(10,4-i); // i = 1 => +1000 (pow 3), i = 4 => +1 (pow 0)   
            }
            else
            {
              nAdd = -pow(10,4-(i-5));
            }
            rCirc += nAdd;
          }
        } // if idx_element != -1
        
      } // if bPressed

      render_screen(20,23,rCirc,nLocked);
    }

    ++nCptFrame;
    if( nCptFrame > 400)
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
    }
}

/**********************************************************************
  Filename    : Drive LiquidCrystal I2C to display characters
  Description : I2C is used to control the display characters of LCD1602.
  Auther      : www.freenove.com
  Modification: 2022/06/28
**********************************************************************/
#include <LiquidCrystal_I2C.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  if (!i2CAddrTest(0x27)) {
    lcd = LiquidCrystal_I2C(0x3F, 16, 2);
  }
  lcd.init();                // initialize the lcd
  lcd.backlight();           // Turn on backlight // sans eclairage on voit rien...
  lcd.print("hello, world, I'm a long text!");// Print a message to the LCD
}

int bWasLighten = 0;
int timeLastScroll = 0;

void loop() {
  // (note: line 1 is the second row, since counting begins with 0):
  lcd.setCursor(0, 1);// set the cursor to column 0, line 1
  // print the number of seconds since reset:
  lcd.print("Counter: ");
  lcd.print(millis() / 1000);
  int flipflop = (millis()/1000)%10;
  int bLight = flipflop>4;
  
  // every x00ms
  if(millis()-timeLastScroll>500)
  {
    timeLastScroll = millis();
    lcd.scrollDisplayLeft();
  }
/*
  if(bWasLighten!=bLight)
  {
    bWasLighten = bLight;
    if(bLight)
      lcd.backlight();
    else
      lcd.noBacklight();
  }
  */
}

bool i2CAddrTest(uint8_t addr) {
  Wire.begin();
  Wire.beginTransmission(addr);
  if (Wire.endTransmission() == 0) {
    return true;
  }
  return false;
}
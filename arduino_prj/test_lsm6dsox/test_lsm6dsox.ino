#include <arduino.h>

#define ALEX_MSM6DSOX_ALL_DEBUG_CODE
#include "C:\Users\alexa\dev\git\electronoos\arduino_prj\blangle_tft3\Alex_LSM6DSOX.cpp"

Alex_LSM6DSOX * sox1 = 0;

void setup()
{
  Serial.begin(57600);
  sox1 = new Alex_LSM6DSOX("sox_name1");
  if( !sox1->begin_I2C(0x6A) )
  {
    Serial.println("ERR: Can't find imu1!");
    delay(3000);
  }
  else
  {
    Serial.println("INF: Found imu1!");
    sox1->printConfig();
  }
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

long int nCptFrame = 0;
void loop()
{
  Serial.println("avant update");
  sox1->update();
  Serial.println("apres update");

  float angle_db_read = sox1->getDegY();
  bool bErrorDb = false;
  
  if( angle_db_read < -600.f )
  {
    bErrorDb = true;
  }

  //if( nCptFrame%100==0 )
  {
    Serial.print( "angle_db: " ); Serial.println(angle_db_read);
    sox1->printValues();
  }

  nCptFrame += 1;
  countFps();
  delay(500);
}
#include "world.h"
#include "definitions.h"

// Conversion helpers
#define deg2rad (PI/180.0)
#define rad2deg (180.0/PI)


World world;

World::World()
  : motorPins_{ 3,6,11, 2,4,10, 5,7,9 }
  , motorsOrder_{ 8, 5, 2, 4, 3, 0, 7, 1, 6 }
  , phiWires_ { // Parametrage d'origine
                    130.0 *deg2rad,  10.0 *deg2rad, 250.0 *deg2rad, //Section 1 + + -
                    50.0 *deg2rad, 290.0 *deg2rad, 170.0 *deg2rad, //Section 2 - - -
                    330.0 *deg2rad,  90.0 *deg2rad, 210.0 *deg2rad  //Section 3 + + -
              }
              
{

  witchPrint_ = 4; // 1:colors 2:motors 3:motion detection 4: none

  timeFrame_ = 0;
  timePrint_ = 0;
  timeMotion_ = 0;
  timeStopping_ = 0;
  timeEthernet_ = 0;
  timeConfig_ = 0;

  standby_pressed_ = false;
  standby_pressed_last_ = false;
  temp_main_input_last_ = false;
  perm_main_input_last_ = false;
  user_button_pressed_ = false;
  user_button_pressed_last_ = false;

  lastPS_ = true;
  f_status_ = MOVING;

  ethernetAvailable_ = false;

  byte stp_cur_ = 0;   // loop variable for stopping process
  byte stp_mot_ = 9;   // Number of motors to be straightened


  ///////////////////////// MOTORS SECTION /////////////////////////

  //angles[9];

  // Angles = { 210, 170, 250, 290, 50, 130, 90, 10, 330 };

  // Commands parameters
  PHI1_   = 0.0f;
  alpha1_ = 0.0f;
  PHI2_   = 0.0f;
  alpha2_ = 0.0f;
  PHI3_   = 0.0f;
  alpha3_ = 0.0f;
}
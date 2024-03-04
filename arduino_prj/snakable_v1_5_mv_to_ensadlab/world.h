#ifndef _WORLD_H_
#define _WORLD_H_

#include <Arduino.h>

/*
    A structure to store all global variables.
    Our state of the world.
*/

class World
{
  public:
    World();

  public: // crado to put all variables as public, but it's "temporary" to reach a testable version quickly
    
    int witchPrint_; // 1:colors 2:motors 3:motion detection 4: none

    unsigned long timeFrame_;
    unsigned long timePrint_;
    unsigned long timeMotion_;
    unsigned long timeStopping_;
    unsigned long timeEthernet_;
    unsigned long timeConfig_;

    bool standby_pressed_;
    bool standby_pressed_last_;
    bool temp_main_input_last_;
    bool perm_main_input_last_;
    bool user_button_pressed_;
    bool user_button_pressed_last_;

    bool dPerm_, dTemp_, dSleep_m_, dPS_Stop_;
    bool lastPS_;
    byte f_status_;

    bool ethernetAvailable_;

    byte stp_cur_;   // loop variable for stopping process
    byte stp_mot_;   // Number of motors to be straightened

    ///////////////////////// MOTORS SECTION /////////////////////////

    float angles_[9];

    // Motor pins
    const int  motorPins_[9] = { 3,6,11, 2,4,10, 5,7,9 };

    // Motor angles
    const float phiWires_[9];

    /// Negative sign when motor is on right side of cable axis

    const int motorsOrder_[9] = { 8, 5, 2, 4, 3, 0, 7, 1, 6 };
    // Angles = { 210, 170, 250, 290, 50, 130, 90, 10, 330 };

    // Commands parameters
    float PHI1_;
    float alpha1_;
    float PHI2_;
    float alpha2_;
    float PHI3_;
    float alpha3_;

};

extern World world; // a singleton

#endif // _WORLD_H_
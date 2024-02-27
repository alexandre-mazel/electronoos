#ifndef __DEFINITIONS_H__
#define __DEFINITIONS_H__

///////////////////////// HARDWARE configuration /////////////////////////

#define USE_ETHERNET
//#define MOTORS_TEST
//#define NO_PERM_DETECTION
//#define NO_TMP_DETECTION
#define _DEBUG

///////////////////////// HARDWARE GPIO pin assignation /////////////////////////

#define MOTION_PIR_PIN  12
#define STANDBY_PIN     13
#define TEMP_MAIN_PIN   22
#define PERM_MAIN_PIN   23
#define RELAY_PIN       38
#define PS_ON_PIN       39
#define CONFIG_LED_PIN  46
#define STOPPED_LED_PIN 47
#define STANDBY_LED_PIN 48
#define USER_BUTTON_PIN 49
#define ETH_CS_PIN      53

// 
//#define SERVO_TIM_PWM_FREQ 50

///////////////////////// CONSTANTS /////////////////////////

#define PRJ_NAME          "SNAKABLE 2021"
#define PRJ_CRED          "ENSADLAB, FEMTO-ST/AS2M"
#define PRJ_DEV           "François MARIONNET"
#define DEV_RELEASE       "1.2.3"
#define DEV_REL_DATE      "04/15/2023"

#define TIME_INCREMENT_TO_RESET 200
#define TIME_BEFORE_MOVING_MOTORS 300
#define TIME_BEFORE_POWERING_MOTORS 50
#define TIME_FRAME_PERIOD 50
#define TIME_ETHERNET_PERIOD 100
#define TIME_PRINT_PERIOD 50
#define TIME_MOTION_PERIOD 100
#define TIME_MOTION_INC (int)(1000 / TIME_MOTION_PERIOD)

///////////////////////// DATA STRUCTURES /////////////////////////

enum STATUS {
  STOPPED = 0,      // Default value
  MOVING,
  STOPPING
};

enum CMD {
  GET_STATUS = 0,   // Default value
  GET_ETH_MODE
} cmd;

enum ERRCODE {
  OK = 0,           // Default value
  WRN_0,
  ERR_0
} errcode;

///////////////////////// GLOBAL VARIABLES /////////////////////////

int witchPrint = 4; // 1:colors 2:motors 3:motion detection 4: none

unsigned long timeFrame = 0;
unsigned long timePrint = 0;
unsigned long timeMotion = 0;
unsigned long timeStopping = 0;
unsigned long timeEthernet = 0;
unsigned long timeConfig = 0;

bool standby_pressed = false;
bool standby_pressed_last = false;
bool temp_main_input_last = false;
bool perm_main_input_last = false;
bool user_button_pressed = false;
bool user_button_pressed_last = false;

bool dPerm, dTemp, dSleep_m, dPS_Stop;
bool lastPS = true;
byte f_status = MOVING;

bool ethernetAvailable;

byte stp_cur = 0;   // loop variable for stopping process
byte stp_mot = 9;   // Number of motors to be straightened

// Conversion helpers
const double deg2rad = PI/180.0;
const double rad2deg = 180.0/PI;

///////////////////////// MOTORS SECTION /////////////////////////

float angles[9];

// Motor pins
const int  motorPins[9] = { 3,6,11, 2,4,10, 5,7,9 };

// Motor angles
const float phiWires[9] ={ // Parametrage d'origine
    130.0 *deg2rad,  10.0 *deg2rad, 250.0 *deg2rad, //Section 1 + + -
     50.0 *deg2rad, 290.0 *deg2rad, 170.0 *deg2rad, //Section 2 - - -
    330.0 *deg2rad,  90.0 *deg2rad, 210.0 *deg2rad  //Section 3 + + -
};
/// Negative sign when motor is on right side of cable axis

const int motorsOrder[9] = { 8, 5, 2, 4, 3, 0, 7, 1, 6 };
// Angles = { 210, 170, 250, 290, 50, 130, 90, 10, 330 };

// Commands parameters
float PHI1   = 0.0f;
float alpha1 = 0.0f;
float PHI2   = 0.0f;
float alpha2 = 0.0f;
float PHI3   = 0.0f;
float alpha3 = 0.0f;

#endif // __DEFINITIONS_H__

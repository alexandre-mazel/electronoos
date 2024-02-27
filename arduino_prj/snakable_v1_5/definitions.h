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

#define PRJ_NAME          "SNAKABLE 2024"
#define PRJ_CRED          "ENSADLAB, FEMTO-ST/AS2M"
#define PRJ_DEV           "François MARIONNET & Alexandre MAZEL"
#define DEV_RELEASE       "1.5"
#define DEV_REL_DATE      "xx/02/2023"

// If changeable by the program, should be moved to config
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

typedef enum CMD {
  GET_STATUS = 0,   // Default value
  GET_ETH_MODE
} _cmd;
extern _cmd cmd;

typedef enum ERRCODE {
  OK = 0,           // Default value
  WRN_0,
  ERR_0
} _errcode;

extern _errcode errcode;

#endif // __DEFINITIONS_H__

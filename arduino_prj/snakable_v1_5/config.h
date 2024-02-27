#ifndef _CONFIG_H_
#define _CONFIG_H_

#include <Arduino.h>
#include "ethernet_srv.h"

// Structure of datas stored into Arduino's EEPROM
typedef union eepromData{
  struct {
    uint8_t  adm_SleepModeDelay = 12;       // x  10 s  = 2 min - No visitor delay before sleeping
    uint8_t  adm_TimeConfigDelay = 6;       // x 500 ms = 3 sec
    uint8_t  usb_SpeedIndex = 1; // note used!
    uint8_t  usb_Timeout = 10;
    uint8_t  eth_MAC[6] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
    uint8_t  eth_Mode = ETH_DHCP;
    uint32_t eth_IP = IPAddress(192, 168, 0, 55);
    uint32_t eth_Subnet = IPAddress(255, 255, 255, 0);
    uint32_t eth_Gateway = IPAddress(192, 168, 0, 1);
    uint32_t eth_DNS = IPAddress(192, 168, 0, 1);
    uint16_t eth_SrvDefaultPort = 80;
    uint8_t  eth_UpdatePeriod = 4;          // WWW monitoring refresh period (x 50 ms)
    bool     eth_ProxyEnable = false;
    uint32_t eth_ProxyIP = IPAddress(192, 168, 0, 1);
    uint16_t eth_ProxyPort = 3128;
    uint8_t  sim_f_vClrSens[4] = { 100, 100, 100, 100 };
    uint8_t  mot_RstIncrement = 3;          // Motors angle increment (in degrees) when resetting to straight line
    float    mot_SectionCoef[3] = { 2.6f, 3.0f, 3.0f };
    float    mot_DefaultAngle[9] = { 78.0, 86.0, 112.0, 85.0, 88.0, 90.0, 88.0, 95.0, 85.0 };
    float    mot_DefaultAngleSetting[9] = { 78.0, 86.0, 112.0, 85.0, 88.0, 90.0, 88.0, 95.0, 85.0 };
    bool     mot_MotorsAngleSetting = false;
  };
  uint8_t raw[97];
} _cfg;

extern _cfg cfg;


#endif // _CONFIG_H_

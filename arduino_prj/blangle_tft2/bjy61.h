#include <Adafruit_Crickit.h>
#include <Adafruit_NeoKey_1x4.h>
#include <Adafruit_NeoTrellis.h>
#include <Adafruit_TFTShield18.h>
#include <Adafruit_miniTFTWing.h>
#include <Adafruit_seesaw.h>
#include <seesaw_motor.h>
#include <seesaw_neopixel.h>
#include <seesaw_servo.h>
#include <seesaw_spectrum.h>

// Handle BJY61 angle reading on an arduino using serial3 for read and serial0 for debug
// v0.7: as external files
// based on: https://www.scribd.com/document/276841798/JY-61-MPU6050-module-User-Manual-by-Elecmaster
// bought from: https://www.amazon.fr/gp/product/B01LXXHUDR/ref=oh_aui_detailpage_o03_s00?ie=UTF8&psc=1

#ifndef _BJY62_H_
#define _BJY62_H_

void bjy_init();
void bjy_receiveBytes(int nNumSensor, signed short s);
void bjy_update(void);
void bjy_displayLastAngles(void);
int bjy_getAngle(int nIndex); // return angle in degrees * 10

#endif // _BJY62_H_
////////////////////////////./////////////////////////////////
//                      SNAKABLE 2021                       //
//                    ENSAD / FEMTO-ST                      //
//                        V 1.2.3                           //
//                       Apr 15 2023                        //
//////////////////////////////////////////////////////////////

#include "definitions.h"

///////////////////////// INCLUDES /////////////////////////

#include "motor.h"
Motor* motors[9];

#include "color_sensor.h"
ColorSensor colorSensor;

#include "serial_parser.h"
SerialParser serialInput;

#include "behavior.h"
Behavior behavior;

#include "config.h"

#include "world.h"

#include "ethernet_srv.h"
EthernetSrv ethSrv;



#include "eeprom_mgmt.h"
eeprom_mgmt eeprom;

#include "motion_detection.h"
MotionDetection motion = MotionDetection(MOTION_PIR_PIN, cfg.adm_SleepModeDelay); // Sleep mode after SLEEP_MODE_DELAY * 10s check interval


void gpioInit() {
  // Motors PWM pins declaration
  for(int i = 0; i < 9; i++){
    pinMode(world.motorPins_[i], OUTPUT);
    digitalWrite(world.motorPins_[i], LOW);
  }
  // Temporary main supply pin declaration
  pinMode(TEMP_MAIN_PIN, INPUT_PULLUP);
  // Permamnent main supply pin declaration
  pinMode(PERM_MAIN_PIN, INPUT_PULLUP);
  // Motors power supply 220V relay pin declaration
  pinMode(RELAY_PIN, OUTPUT);
  // Motors power supply PS_ON pin declaration
  pinMode(PS_ON_PIN, OUTPUT);
  gpioMotorsPS(false);
  // User led pin declaration
  pinMode(CONFIG_LED_PIN, OUTPUT);
  digitalWrite(CONFIG_LED_PIN, LOW);
  pinMode(STOPPED_LED_PIN, OUTPUT);
  digitalWrite(STOPPED_LED_PIN, LOW);
  // Standby pushbutton pin declaration
  pinMode(STANDBY_PIN, INPUT_PULLUP);
  // User pushbutton pin declaration
  pinMode(USER_BUTTON_PIN, INPUT_PULLUP);
}

void printProjectVersion() {
  Serial.flush();
  Serial.print("Project name  : "); Serial.println(PRJ_NAME);
  Serial.print("Project team  : "); Serial.println(PRJ_CRED);
  Serial.print("Release       : "); Serial.println(DEV_RELEASE);
  Serial.print("Release date  : "); Serial.println(DEV_REL_DATE);
  Serial.println("===================================================");
  Serial.println("Entering SETUP");
  Serial.print  ("Configuration data retreived from EEPROM on startup : CRC ");
  if (eeprom.dataFactoryDefaulted) Serial.print("FAILED\nEEPROM cleared and initialized with factory default values\nNew CRC ");
  Serial.println(eeprom.isCrcValid ? "VALID" : "INVALID");

  Serial.print("\nSection amplitude coefficients = {");
  for (byte i = 0; i < 3; i++) {
    if (i) Serial.print(",");
    Serial.print(" "); Serial.print(cfg.mot_SectionCoef[i], 1);
  }
  Serial.print(" }\nMotors default angles = {");
  for (byte i = 0; i < 9; i++) {
    if (i) Serial.print(",");
    Serial.print(" "); Serial.print(cfg.mot_DefaultAngle[i], 1);
  }
  Serial.println(" }\n");
}

void setStatus(STATUS new_status) {
  ethData.state = new_status;
  switch (ethData.state) {
    case STOPPED: digitalWrite(STOPPED_LED_PIN, HIGH); Serial.println("STOPPED"); break;
    case MOVING: digitalWrite(STOPPED_LED_PIN, LOW); Serial.println("MOVING"); break;
    case STOPPING: Serial.println(cfg.mot_MotorsAngleSetting ? "RESETTING" : "STOPPING"); break;
  }
}

void setFStatus(STATUS new_status) {
  world.f_status_ = new_status;
  switch (world.f_status_) {
    case STOPPED: Serial.println("FORCED - STOPPED"); break;
    case MOVING: Serial.println("FORCED - MOVING"); break;
    case STOPPING: Serial.println("FORCED - STOPPING"); break;
  }
}

void printMotors(){
  for(int i = 0; i < 9; i++) {
    if (world.angles_[i] < 100) Serial.print(" ");
    if (world.angles_[i] < 10) Serial.print(" ");
    Serial.print(world.angles_[i]);
    Serial.print(" ");
  }
  Serial.println("");
}


//=============== SETUP ==============
void setup() {
#ifndef MOTORS_TEST
  eeprom.initializeVariables();
#endif
  gpioInit();
  //eeprom.writeEeprom((uint8_t)offsetof(union eepromData, mot_MotorsAngleSetting), cfg.mot_MotorsAngleSetting = true);
 
  // Serial link parameters
  Serial.begin(1000000L); // Alma was: cfg.usb_SpeedIndex
  Serial.setTimeout(cfg.usb_Timeout);

  printProjectVersion();
  
  world.user_button_pressed_ = !digitalRead(USER_BUTTON_PIN);
  if (world.user_button_pressed_) {
    Serial.println("User button pressed !");
    Serial.println("Rewriting EEPROM with default values !");
    eeprom.storeFactoryDefaultValues();
    Serial.println("Done !!");
    world.user_button_pressed_last_ = true;
  }
  
  Serial.println(cfg.mot_MotorsAngleSetting ? "!!! CONFIG mode detected. RESETTING motors angles !!!" : "NORMAL mode");
  setStatus(cfg.mot_MotorsAngleSetting ? STOPPING : STOPPED);

  // Motors declaration and angles initialization
  for (int i = 0; i < 9; i++) {
    motors[i] = new Motor();
    motors[i]->init(world.motorPins_[i], world.angles_[i] = ((cfg.mot_MotorsAngleSetting) ? cfg.mot_DefaultAngleSetting[i] : cfg.mot_DefaultAngle[i]));
  }
#ifndef MOTORS_TEST
  // Color sensor initialization
  colorSensor.init();

  // Pseudo random generator initialization
  randomSeed(analogRead(7));

#ifdef USE_ETHERNET
  // Ethernet server initialization
  ethSrv.init();
#endif

  // Behavior class initialization
  behavior.init();

  Serial.println("Leaving SETUP to enter loop()\n");
#endif
#ifdef MOTORS_TEST
  float tst_DefaultAngle[9] = { 78.0, 86.0, 112.0, 85.0, 88.0, 90.0, 88.0, 95.0, 85.0 };
// + + - - - - + + -   Pour détendre, si -, diminuer l'angle, sinon l'augmenter
//{ 8, 5, 2, 4, 3, 0, 7, 1, 6 };
// Angles = { 210, 170, 250, 290, 50, 130, 90, 10, 330 };

  for (int i = 0; i < 9; i++)
//    motors[motorsOrder[i]]->goAngle(cfg.mot_DefaultAngle[motorsOrder[i]]);
    motors[i]->goAngle(tst_DefaultAngle[i]);
  delay(200);
  gpioMotorsPS(true);
  delay(1000);
/*  for (int i = 0; i < 9; i++) {
    Serial.println(i);
    motors[motorsOrder[i]]->goAngle(cfg.mot_DefaultAngle[motorsOrder[i]] - 4);
    delay(500);
    motors[motorsOrder[i]]->goAngle(cfg.mot_DefaultAngle[motorsOrder[i]]);
    delay(500);
    motors[motorsOrder[i]]->goAngle(cfg.mot_DefaultAngle[motorsOrder[i]] + 4);
    delay(500);
    motors[motorsOrder[i]]->goAngle(cfg.mot_DefaultAngle[motorsOrder[i]]);
    delay(500);
  }*/
  gpioMotorsPS(false);
  delay(500);
#endif
}




//=============== LOOP ==============

void loop(){
#ifdef MOTORS_TEST
  return;
#endif

  // Process Ethernet commands and requests
#ifdef USE_ETHERNET
  if ((millis() - world.timeEthernet_) >= TIME_ETHERNET_PERIOD) {
    world.timeEthernet_ = millis();
    ethSrv.process();
  }
#endif

  // Get standby pushbutton status and set standby mode
  world.standby_pressed_ = !digitalRead(STANDBY_PIN);
  if (world.standby_pressed_ && !world.standby_pressed_last_) {
	  ethData.stdby_m = !ethData.stdby_m;
    digitalWrite(STANDBY_LED_PIN, ethData.stdby_m);
    Serial.print("Standby ");
    Serial.println(ethData.stdby_m ? "ON" : "OFF");
  }
  world.standby_pressed_last_ = world.standby_pressed_;

#ifdef NO_TMP_DETECTION
  ethData.temp = true;
#else
  // Get temporary mains voltage status
  ethData.temp = !digitalRead(TEMP_MAIN_PIN);
  if (ethData.temp != world.temp_main_input_last_) {
    world.temp_main_input_last_ = ethData.temp;
    Serial.print("Tmp mains input ");
    Serial.println(ethData.temp ? "ON" : "OFF");
  }
#endif

  // Get permanent mains voltage status
#ifdef NO_PERM_DETECTION
  ethData.perm = true;
#else
  ethData.perm = !digitalRead(PERM_MAIN_PIN);
  if (ethData.perm != world.perm_main_input_last_) {
    world.perm_main_input_last_ = ethData.perm;
    Serial.print("Perm mains input ");
    Serial.println(ethData.perm ? "ON" : "OFF");
  }
#endif

  world.user_button_pressed_ = !digitalRead(USER_BUTTON_PIN);
  if (world.user_button_pressed_ && !world.user_button_pressed_last_) {
    ethData.user_m = !ethData.user_m;
    Serial.print("User mode ");
    Serial.println(ethData.user_m ? "ON" : "OFF");
  }
  world.user_button_pressed_last_ = world.user_button_pressed_;

  // Get motion detection sensor status and set sleep mode every TIME_MOTION_PERIOD ms
  if ((millis() - world.timeMotion_) >= TIME_MOTION_PERIOD) {
    world.timeMotion_ = millis();
    // Check motion sensor
    motion.update();
    //ethData.pir = motion.pir; // TODO update datas here
    //ethData.pir_cnt = motion.count;
    // Enable / disable sleep_mode based on the current value
    //ethData.sleep_m = motion.sleep_mode;
  }

  world.dPerm_ = (frc.f_mPerm) ? frc.f_vPerm : ethData.perm;
  world.dTemp_ = (frc.f_mTemp) ? frc.f_vTemp : ethData.temp;
  world.dSleep_m_ = (frc.f_mSleep_m) ? frc.f_vSleep_m : ethData.sleep_m;
  world.dPS_Stop_ = (frc.f_mRelay && !frc.f_vRelay) || (frc.f_mPS_ON && !frc.f_vPS_ON);

  // Check if system has to be switched off
  if (((ethData.state == MOVING) && (!world.dTemp_ || !world.dPerm_ || world.dSleep_m_ || ethData.stdby_m || (ethData.mode & 2))) || ((world.f_status_ == MOVING) && world.dPS_Stop_)) {
    // Stop the behavior
    behavior.stop();
	  // Update status
    if ((world.f_status_ == MOVING) && world.dPS_Stop_)
      setFStatus(STOPPING);
    else
      setStatus(STOPPING);
  }
  else if (((ethData.state == STOPPED) && world.dTemp_ && world.dPerm_ && !world.dSleep_m_ && !ethData.stdby_m && ((ethData.mode & 2) == 0)) || ((world.f_status_ == STOPPED) && !world.dPS_Stop_)) {
    // Motors angles update - but should already be defaulted
    for (int i = 0; i < 9; i++) {
      motors[i]->goAngle(cfg.mot_DefaultAngle[i]);
    }
	  // Supply motors ON & update status
    if ((world.f_status_ == STOPPED) && !world.dPS_Stop_) {
      setFStatus(MOVING);
      _gpioMotorsPS();
    } else {
      setStatus(MOVING);
      gpioMotorsPS(true);
    }
    // Start the behavior
    if ((ethData.state == MOVING) && (world.f_status_ == MOVING)) {
      behavior.init();
      behavior.start();
    }
    //delay(50);
  }

  if ((ethData.state == STOPPING) || (world.f_status_ == STOPPING)) {
    if (millis() - world.timeStopping_ > TIME_INCREMENT_TO_RESET) {
      world.timeStopping_ = millis();
      if (((ethData.state == STOPPING) && (world.f_status_ == STOPPED)) || ((ethData.state == STOPPED) && (world.f_status_ == STOPPING)))
        world.stp_mot_ = 0;
      else {
        Serial.print("   ");
        if (abs(world.angles_[world.stp_cur_] - cfg.mot_DefaultAngle[world.stp_cur_]) <= cfg.mot_RstIncrement) {
          world.angles_[world.stp_cur_] = cfg.mot_DefaultAngle[world.stp_cur_];
          world.stp_mot_--;
        }
        else {
          if (world.angles_[world.stp_cur_] > cfg.mot_DefaultAngle[world.stp_cur_])
            world.angles_[world.stp_cur_] -= cfg.mot_RstIncrement;
          else
            world.angles_[world.stp_cur_] += cfg.mot_RstIncrement;
        }
        digitalWrite(STOPPED_LED_PIN, !digitalRead(STOPPED_LED_PIN));
        motors[world.stp_cur_]->goAngle(world.angles_[world.stp_cur_]);
        if (world.angles_[world.stp_cur_] < 100) Serial.print(" ");
        if (world.angles_[world.stp_cur_] < 10) Serial.print(" ");
        Serial.print(world.angles_[world.stp_cur_]);
        Serial.print(" ");

        if (++world.stp_cur_ == 9) {
          Serial.println();
          world.stp_cur_ = 0;
          if (world.stp_mot_) world.stp_mot_ = 9;
        }
      }
      if (world.stp_mot_ == 0) {
        Serial.println("Done !");
        // Switch off motors supply relay
        if (world.f_status_ == STOPPING) {
          setFStatus(STOPPED);
          _gpioMotorsPS();
        } else {
          setStatus(STOPPED);
          gpioMotorsPS(false);
        }
        if (cfg.mot_MotorsAngleSetting) {
          eeprom.writeEeprom(offsetof(union eepromData, mot_MotorsAngleSetting), cfg.mot_MotorsAngleSetting = false);
          Serial.println("MODE NORMAL");
        }
        if (ethData.mode & 2) {
          Serial.println("MODE CONFIG ready");
        }
        world.stp_mot_ = 9;
      }
    }
  }

  // Process serial commands
  serialCmd();

  // if not moving, just return
  if ((ethData.state != MOVING) || (world.f_status_ != MOVING)) {
    return;
  }

  // Get color sensor value update
  if ((millis() - world.timeFrame_) >= TIME_FRAME_PERIOD) {
    world.timeFrame_ = millis(); 
    colorSensor.update();
    //behavior.setDeltaLight() = colorSensor.deltaLight; // TODO alma: update in behavior
  }

  behavior.update(millis(),colorSensor);

/*
  // todo Alma: uncomment this block

  alpha1 = behavior.sections[0].alpha;
  PHI1   = behavior.sections[0].phi;
  alpha2 = behavior.sections[1].alpha;
  PHI2   = behavior.sections[1].phi;
  alpha3 = behavior.sections[2].alpha;
  PHI3   = behavior.sections[2].phi;

  // -------- motors angles calculation ------------
  //section 1
  world.angles_[0] = cfg.mot_DefaultAngle[0] + (cfg.mot_SectionCoef[0] * motors[0]->calculMoteur(PHI1, alpha1, phiWires[0])); 
  world.angles_[1] = cfg.mot_DefaultAngle[1] + (cfg.mot_SectionCoef[0] * motors[1]->calculMoteur(PHI1, alpha1, phiWires[1]));
  world.angles_[2] = cfg.mot_DefaultAngle[2] - (cfg.mot_SectionCoef[0] * motors[2]->calculMoteur(PHI1, alpha1, phiWires[2]));
 
  //section 2
  world.angles_[3] = cfg.mot_DefaultAngle[3] - (cfg.mot_SectionCoef[1] * motors[3]->calculMoteur(PHI2, alpha2, phiWires[3]));
  world.angles_[4] = cfg.mot_DefaultAngle[4] - (cfg.mot_SectionCoef[1] * motors[4]->calculMoteur(PHI2, alpha2, phiWires[4]));
  world.angles_[5] = cfg.mot_DefaultAngle[5] - (cfg.mot_SectionCoef[1] * motors[5]->calculMoteur(PHI2, alpha2, phiWires[5]));

  //section 3
  world.angles_[6] = cfg.mot_DefaultAngle[6] + (cfg.mot_SectionCoef[2] * motors[6]->calculMoteur(PHI3, alpha3, phiWires[6]));
  world.angles_[7] = cfg.mot_DefaultAngle[7] + (cfg.mot_SectionCoef[2] * motors[7]->calculMoteur(PHI3, alpha3, phiWires[7]));
  world.angles_[8] = cfg.mot_DefaultAngle[8] - (cfg.mot_SectionCoef[2] * motors[8]->calculMoteur(PHI3, alpha3, phiWires[8]));

  // Motors angles update
  for(int i = 0; i < 9; i++){
    motors[i]->goAngle(world.angles_[i]);
  }

  // Serial print management
  if ((millis() - timePrint) > TIME_PRINT_PERIOD){
    timePrint = millis();
    switch(world.witchPrint_){
      case 1: colorSensor.printColor(); break;      
      case 2: printMotors(); break;
      case 3: motionDetection.print(); break;
    }
  }
  */
}

//======================================================
//                    FUNCTIONS
//======================================================

// Function to let the cable return to straight position by 'increment' degrees every 'time_increment_to_reset' ms
//------------------------------------
// Serial commands format : cmd,params
void serialCmd(){
  /*  */
  char* str = serialInput.readLine();
  while (str != NULL) {
    char* cmd = serialInput.getStr();
    if (strcmp(cmd, "play") == 0) {
      float p1 = serialInput.getFloat();
      float a1 = serialInput.getFloat();
      float p2 = serialInput.getFloat();
      float a2 = serialInput.getFloat();
      float p3 = serialInput.getFloat();
      float a3 = serialInput.getFloat();
      if(!isnan(p1)) world.PHI1_   = p1;
      if(!isnan(a1)) world.alpha1_ = a1;
      if(!isnan(p2)) world.PHI2_   = p2;
      if(!isnan(a2)) world.alpha2_ = a2;
      if(!isnan(p3)) world.PHI3_   = p3;
      if(!isnan(a3)) world.alpha3_ = a3;
    }
    else if (strcmp(cmd, "beh") == 0) {
      behavior.stop();
	    setStatus(STOPPING);
    }
    else if (strcmp(cmd, "lc") == 0) {
      float p1 = serialInput.getFloat();
      if (isnan(p1)) p1 = 0.92f;
      colorSensor.setLightCoef(p1);
    }
    else if (strcmp(cmd, "$") == 0) {
      behavior.stop();
	    setStatus(STOPPING);
    }
    else if (strcmp(cmd, "print") == 0) {
      float p1 = serialInput.getFloat();
      if (!isnan(p1))
        world.witchPrint_ = (int)p1;
    }
/*    else if (strcmp(cmd, "test_m") == 0) {
      if (!ethData.stdby_m) return;
      byte a;
      Serial.println("Entering motors test sequence");
      for (a = 0; a < 9; a++) {
          motors[a]->goAngle(cfg.mot_DefaultAngle[motorsOrder[a]]);
      }
      delay(300);
      gpioMotorsPS(true);
      delay(300);
      for (a = 0; a < 9; a++) {
        char inc = (a < 5) ? 3 : -3;
        Serial.print("Angle : ");
        Serial.print(cfg.mot_DefaultAngle[motorsOrder[a]]);
        if (inc) Serial.print("+");
        Serial.println(inc);
        motors[a]->goAngle(cfg.mot_DefaultAngle[motorsOrder[a]] - inc);
        delay(500);
        Serial.print("Angle ");
        Serial.print(cfg.mot_DefaultAngle[motorsOrder[a]]);
        motors[a]->goAngle(cfg.mot_DefaultAngle[motorsOrder[a]]);
        delay(500);
        motors[a]->goAngle(cfg.mot_DefaultAngle[motorsOrder[a]] + inc);
        delay(500);
        motors[a]->goAngle(cfg.mot_DefaultAngle[motorsOrder[a]]);
        delay(500);
      }
    }*/
    else {
      //behavior.serialCmd(cmd); // TODO Alma
    }
    str = serialInput.readLine(); 
  }
}

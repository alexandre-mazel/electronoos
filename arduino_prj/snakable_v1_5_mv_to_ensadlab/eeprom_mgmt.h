#ifndef __EEPROM_MGMT_H__
#define __EEPROM_MGMT_H__

#include <EEPROM.h>

/* EEPROM MEMORY SPACE
 *  EEPROM_DATA_VALIDITY    Byte    0   0
 *    
 *    Serial parameters data
 *    Ethernet parameters data
 *    Motors sections parameters data
 *    PIR parameters data
 *    Light sensor parameters data
 *    Behavior parameters data
 */

class eeprom_mgmt {
  public:
    eeprom_mgmt() {
      isCrcValid = checkCRC();
    }
    boolean isCrcValid;
    boolean dataFactoryDefaulted = false;

    // universal eeprom WRITE
    template <class T> void writeEeprom(uint8_t addr, T value, bool writeCRC = true) {
        uint8_t x;
        uint8_t *ptr;
    
        x = sizeof(T);
        ptr = (uint8_t *)(void *)&value;
    
        while (x--) {
            eeprom_write_byte((addr + x), *(ptr + x));
        }
        if (writeCRC) setCRC();
    }

    unsigned long calculatedCRC() {
      const unsigned long crc_table[16] =
      {
        0x00000000, 0x1db71064, 0x3b6e20c8, 0x26d930ac,
        0x76dc4190, 0x6b6b51f4, 0x4db26158, 0x5005713c,
        0xedb88320, 0xf00f9344, 0xd6d6a3e8, 0xcb61b38c,
        0x9b64c2b0, 0x86d3d2d4, 0xa00ae278, 0xbdbdf21c
      };
      unsigned long crc = ~0L;      
      for (int index = 0; index < EEPROM.length() - 4; ++index) {
        crc = crc_table[(crc ^ EEPROM[index]) & 0x0f] ^ (crc >> 4);
        crc = crc_table[(crc ^ (EEPROM[index] >> 4)) & 0x0f] ^ (crc >> 4);
        crc = ~crc;
      }
      return crc;
    }

    unsigned long storedCRC() {
      unsigned long storedCrc;
      EEPROM.get(EEPROM.length() - 4, storedCrc);
      return storedCrc;
    }

    boolean checkCRC() {
      return (storedCRC() == calculatedCRC());
    }

    void setCRC() {
      EEPROM.put(EEPROM.length() - 4, calculatedCRC());
    }

    void initializeVariables() {
      if (isCrcValid)
        EEPROM.get(0, cfg);
      else
        storeFactoryDefaultValues();
    }

    void storeFactoryDefaultValues() {
      dataFactoryDefaulted = true;
      Serial.println("Clearing Arduino's EEPROM");

      for (int i = 0 ; i < EEPROM.length() ; i++) EEPROM.write(i, 0);
      Serial.println("Arduino's EEPROM cleared");
      Serial.println("Storing factory default values into Arduino's EEPROM");

      cfg.adm_SleepModeDelay = 12;       // x  10 s  = 2 min - No visitor delay before sleeping
      cfg.adm_TimeConfigDelay = 6;       // x 500 ms = 3 sec
      //cfg.usb_SpeedIndex = _1000000;
      cfg.usb_Timeout = 10;
      uint8_t eth_MAC[8] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
      memcpy(cfg.eth_MAC, eth_MAC, sizeof(eth_MAC));
      cfg.eth_Mode = ETH_DHCP;
      cfg.eth_IP = IPAddress(192, 168, 0, 55);
      cfg.eth_Subnet = IPAddress(255, 255, 255, 0);
      cfg.eth_Gateway = IPAddress(192, 168, 0, 1);
      cfg.eth_DNS = IPAddress(192, 168, 0, 1);
      cfg.eth_SrvDefaultPort = 80;
      cfg.eth_UpdatePeriod = 4;          // WWW monitoring refresh period (x 50 ms)
      cfg.eth_ProxyEnable = false;
      cfg.eth_ProxyIP = IPAddress(192, 168, 0, 1);
      cfg.eth_ProxyPort = 3128;
      float DefaultAngle[9] = { 78.0, 86.0, 112.0, 85.0, 88.0, 90.0, 88.0, 95.0, 85.0 };
      memcpy(cfg.mot_DefaultAngle, DefaultAngle, sizeof(DefaultAngle));
      memcpy(cfg.mot_DefaultAngleSetting, DefaultAngle, sizeof(DefaultAngle));
      float mot_SectionCoef[3] = { 2.6f, 3.0f, 3.0f };
      memcpy(cfg.mot_SectionCoef, mot_SectionCoef, sizeof(mot_SectionCoef));
      cfg.mot_RstIncrement = 3;        // Motors angle increment (in degrees) when resetting to straight line
      cfg.mot_MotorsAngleSetting = false;
      uint8_t sim_f_vClrSens[4] = { 100, 100, 100, 100 };
      memcpy(cfg.sim_f_vClrSens, sim_f_vClrSens, sizeof(sim_f_vClrSens));

      EEPROM.put(0, cfg);
      setCRC();
      Serial.println("Factory default values stored into Arduino's EEPROM");
      Serial.println("Checking EEPROM's CRC");
      isCrcValid = checkCRC();
      Serial.print("EEPROM's CRC check ");
      Serial.println(isCrcValid ? "PASSED" : "FAILED");
      //Serial.print("New USB serial speed : "); Serial.println(index2Speed(cfg.usb_SpeedIndex));
      Serial.print("New USB timeout      : "); Serial.println(cfg.usb_Timeout);
      Serial.end();
      //Serial.begin(index2Speed(cfg.usb_SpeedIndex));
      Serial.setTimeout(cfg.usb_Timeout);
    }

    void storeDataAsDefault() {
      Serial.println("Storing current values as default into Arduino's EEPROM");
      EEPROM.put(0, cfg);
      setCRC();
      Serial.println("Current values stored as default into Arduino's EEPROM");
      Serial.println("Checking EEPROM's CRC");
      isCrcValid = checkCRC();
      Serial.print("EEPROM's CRC check ");
      Serial.println(isCrcValid ? "PASSED" : "FAILED");
    }
};

#endif

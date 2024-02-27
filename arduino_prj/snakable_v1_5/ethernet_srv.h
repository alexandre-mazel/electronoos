#ifndef __ETHERNET_SRV_H__
#define __ETHERNET_SRV_H__

#include <Arduino.h>
#include <SPI.h>
#include <Ethernet.h>

#define ETH_DHCP_TIMEOUT       3000  // 3s, factory default value (or no parameter value) is 60000
#define ETH_DHCP_RESP_TIMEOUT  2000  // 2s (= factory default value (or no parameter value))
#define TIME_INACTIVE_CLIENT   1000

typedef enum MODE {
  NORMAL = 0,       // Default value
  CONFIG_DEBUG,
  CONFIG_PARAMS,
  CONFIG_MOTORS
} _mode;

enum EthMode {
  ETH_DHCP = 0,
  ETH_STATIC_IP
};

enum BROWSER{
  UNDEFINED = 0,
  FIREFOX,
  CHROME,
  IE,
  EDGE,
  OPERA,
  SAFARI
};

// Structure of datas sent to supervision web page
typedef union {
  struct {
    boolean perm       : 1;  //     0            R   W
    boolean temp       : 1;  //     1            R   W
    boolean pir        : 1;  //     2            R   W
    boolean ps_relay   : 1;  //     3            R   W
    boolean ps_on      : 1;  //     4            R   W
    boolean sleep_m    : 1;  //     5            RW  W
    boolean stdby_m    : 1;  //     6            RW
    boolean user_m     : 1;  //     7            RW  W
  
    boolean f_oRelay   : 1;
    boolean f_oPS_ON   : 1;
    uint8_t mode       : 2;  //     8 -  9       R
    uint8_t state      : 2;  //    10 - 11       R
    uint8_t none       : 2;

    uint8_t pir_cnt    : 8;  //    16 - 23       R

    uint8_t session    : 8;  //    24 - 31       R
  };
  uint32_t raw = 0;
  uint8_t  byte[4];
} _ethData;

extern _ethData ethData;


typedef union {
  struct {
    uint8_t f_mPerm    : 1;
    uint8_t f_vPerm    : 1;
    uint8_t f_mTemp    : 1;
    uint8_t f_vTemp    : 1;
    uint8_t f_mPir     : 1;
    uint8_t f_vPir     : 1;
    uint8_t f_mSleep_m : 1;
    uint8_t f_vSleep_m : 1;
    boolean f_mRelay   : 1;
    boolean f_vRelay   : 1;
    boolean f_mPS_ON   : 1;
    boolean f_vPS_ON   : 1;
    uint8_t none       : 4;
  };
  uint16_t   forcedParams = 0;
} _frc;

extern _frc frc;

void gpioMotorsPS(bool on);
void _gpioMotorsPS();

class EthernetSrv {
	public:
		EthernetSrv();

		void init();

    void setSTDBY(bool new_value);
    void process();

  private:
    EthernetServer server_;
    char chaine_[200];
    byte cur_ = 0;

};
#endif

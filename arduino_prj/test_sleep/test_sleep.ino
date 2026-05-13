//#include <ArduinoLowPower.h> // only for SAMD

#include <LowPower.h>
#include <avr/sleep.h>


void setup() {
  Serial.begin(57600);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(5000);
  digitalWrite(LED_BUILTIN, LOW);

  // for MEGA2560:
  LowPower.idle(SLEEP_8S, ADC_OFF, TIMER5_OFF, TIMER4_OFF, TIMER3_OFF, 
  		  TIMER2_OFF, TIMER1_OFF, TIMER0_OFF, SPI_OFF, USART3_OFF, 
  		  USART2_OFF, USART1_OFF, USART0_OFF, TWI_OFF);

  // =>  0.347w

  // sympa mais ne ressort jamais...
  // => 0.175w
  /*
  set_sleep_mode (SLEEP_MODE_PWR_DOWN);  
  sleep_enable();
  sleep_cpu();  
*/

}

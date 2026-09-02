//
// Temporisation_220v
//
// Goal: 
//    Turn on the delay port, then avec 20 sec, turn it off.
//    
//    Turn it on again for 20 sec, every 10 minutes
//

const int pin_switch = 31;
const int pin_relay = 26;

const int DURATION_KEEP_ON_IN_SEC = 30;
//const int DURATION_TO_REACTIVATE_IN_SEC = 10*60;
const int DURATION_TO_REACTIVATE_IN_SEC = 40; // short time to debug...



unsigned long last_start_sec = 0;
int relay_state = 0;

void setup() 
{
  Serial.begin(57600);

  pinMode( pin_relay, OUTPUT );

  last_start_sec = millis() / 1000;
  relay( 1 );
  

}

void relay( bOn )
{
  digitalWrite( pin_relay, bOn?HIGH:LOW);
  relay_state = bOn;
}


void loop() 
{
  int bPushed = digitalRead(pin_switch) == HIGH;
  unsigned long time_turned_on = (millis()/1000) - last_start_sec;

  Serial.print( "Pushed: " );
  Serial.print( bPushed );
  Serial.print( ", time_turned_on: " );
  Serial.println( time_turned_on );

  if( time_turned_on - last_start > DURATION_TO_REACTIVATE_IN_SEC )
  {
    bPushed = 1; // force to reactivate
  }
  else if( time_turned_on - last_start > DURATION_KEEP_ON_IN_SEC && relay_state )
  {
    relay( 0 );
  }

  if( bPushed )
  {
    last_start_sec = millis() / 1000;
    relay( 1 );
  }


  delay(100);
}

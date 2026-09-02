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

const int DURATION_KEEP_ON_IN_SEC = 20;
const int DURATION_TO_REACTIVATE_IN_SEC = 10*60;
// const int DURATION_TO_REACTIVATE_IN_SEC = 50; // short time to debug...



unsigned long last_start_sec = 0;
int relay_state = 0;

void setup() 
{
  Serial.begin(57600);

  pinMode( pin_relay, OUTPUT );

  Serial.println( "\nTemporisation_220v v0.8\n" );

  Serial.print( "pin_switch: " ); Serial.println( pin_switch );
  Serial.print( "pin_relay: " ); Serial.println( pin_relay );

  Serial.print( "DURATION_KEEP_ON_IN_SEC: " ); Serial.println( DURATION_KEEP_ON_IN_SEC );
  Serial.print( "DURATION_TO_REACTIVATE_IN_SEC: " ); Serial.println( DURATION_TO_REACTIVATE_IN_SEC );



  last_start_sec = millis() / 1000;
  relay( 1 );

  delay( 2000 ); // time to read the debug
}

void relay( int bOn )
{
  Serial.print( "relay set to: " );
  Serial.println( bOn );
  digitalWrite( pin_relay, bOn?LOW:HIGH);
  relay_state = bOn;
}


void loop() 
{
  int bPushed = digitalRead(pin_switch) == HIGH;
  unsigned long duration_turned_on = (millis()/1000) - last_start_sec;

  Serial.print( "Pushed: " );
  Serial.print( bPushed );
  Serial.print( ", relay_state: " );
  Serial.print( relay_state );
  Serial.print( ", duration_turned_on: " );
  Serial.println( duration_turned_on );

  if( duration_turned_on > DURATION_TO_REACTIVATE_IN_SEC )
  {
    bPushed = 1; // force to reactivate
  }
  else if( duration_turned_on > DURATION_KEEP_ON_IN_SEC && relay_state )
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

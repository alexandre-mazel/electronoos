const int pin_IR = 8; // 8 is for D8

void setup()
{
  Serial.begin(115200);
  Serial.println("Pololu dist IR: begin");
  pinMode(pin_IR, INPUT);
}

int16_t avg_dist = 0;
long int time_last_output = 0;

void loop()
{
  int16_t t = pulseIn(pin_IR, HIGH);
 
  if (t == 0)
  {
    // pulseIn() did not detect the start of a pulse within 1 second.
    Serial.println("timeout");
  }
  else if (t > 1850)
  {
    // No detection.
    Serial.println(-1);
  }
  else
  {
    // Valid pulse width reading. Convert pulse width in microseconds to distance in millimeters.
    int16_t dist = (t - 1000) * 4;
 
    // Limit minimum distance to 0.
    if (dist < 0) { dist = 0; }

    avg_dist = ( avg_dist * 9 + dist * 1 ) / 10;
  

    if( millis()-time_last_output > 1000 )
    {
      time_last_output = millis();
      Serial.print( "dist: " );
      Serial.print( dist );
      Serial.print( ", avg_dist: " ); // NB: le capteur a 6-7 mm d'epaisseur avec son socle. mesure brute: 100mm => 144mm
      Serial.print( avg_dist );
      Serial.println(" mm");
    }
  }

  delay(1);
}

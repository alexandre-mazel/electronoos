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

    // NB: le capteur a 6-7 mm d'epaisseur avec son socle. 
    // mesure brute: different objet a 100mm: boite bleue jlpcb: 144 mm, piece support stepper imprimée en noire: 144, feuille de papier: 160.
    // mesure brute: avec boite bleue jlpcb: 100mm => 144mm; 200 => 332; 300 => 526; 400 => 698; 500 => 873; 600 => 1024; 700 => 1156; 800 => 1269; 900 => 1204

    // soit apres recalibration:
    dist = (dist + 28.416 ) / 1.7241;


    avg_dist = ( avg_dist * 19 + dist * 1 ) / 20; // a 130cm de max, ca fait 1300mm, donc en max pour ne pas depasser int16, il ne faut pas filter a plus de 24
  

    if( millis()-time_last_output > 1000 )
    {
      time_last_output = millis();
      Serial.print( "dist: " );
      Serial.print( dist );
      Serial.print( ", avg_dist: " );
      Serial.print( avg_dist );
      Serial.println(" mm");
    }
  }

  delay(10); // 10 => 100 Hz (le capteur est a 100 Hz minimum)
}

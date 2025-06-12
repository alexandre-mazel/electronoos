#define FIRST_PWM_PIN 8

// Non linear Ramping: input between 0 and 255, same output
// but inputing 128 return around 60
unsigned char nonlinear_ramp(unsigned char input) {
    double gamma = 2.4;  // Exposant, adjusted so the value 128 gives ~60
    double normalized_input = input / 255.0;
    double output = 255.0 * pow(normalized_input, gamma);
    return (unsigned char)(output + 0.5); // arrondi
}

void setup()
{
    Serial.begin( 57600 );

    Serial.println("INF: MOS Cmd v0.3" );

    pinMode( LED_BUILTIN, OUTPUT );

    if( 0 )
    {
        Serial.println( "DBG: Outputting ramping value for setup" );  
        for( int i = 0; i < 256; ++i )
        {
            int n = nonlinear_ramp(i);
            Serial.print("ramping: "); Serial.print( i ); Serial.print(" => "); Serial.println( n );
        }
    }
}

void loop()
{
    if(0)
    {
        // alternate strong and unstrong
        Serial.println("full");
        analogWrite(9, 255);
        delay(5000);
        Serial.println("quarter");
        analogWrite(9, 60);
        delay(5000);
        Serial.println("off");
        analogWrite(9, 0);
        delay(5000);
    }

    if(0)
    {
        Serial.println("ramping...");
        for(int i = 0; i < 256; ++i )
        {
            analogWrite(9, i);
            delay(40); // on 10 sec
        }
    }

    if(0)
    {
        Serial.println("non linear ramping...");
        for(int i = 0; i < 256; ++i )
        {
            analogWrite(9, nonlinear_ramp(i));
            delay(40); // on 10 sec
        }
    }

    if(0)
    {
        Serial.println("slow ramping...");
        analogWrite(9, 0);
        delay(500);
        for(int i = 0; i < 50; ++i )
        {
            analogWrite(9, i);
            delay(200); // on 10 sec
        }
    }

    if(0)
    {
        Serial.println("very slow ramping...");
        analogWrite(9, 0);
        delay(500);
        for(int i = 0; i < 20; ++i )
        {
            analogWrite(9, i);
            delay(1000); // on 20 sec
        }
    }
  
    if(1)
    {
        // alternate strong on every of three
        Serial.println("alternate 3");
        for(int i = 0; i <3; ++i )
        {
            Serial.println(i);
            analogWrite(FIRST_PWM_PIN+i, 255);
            digitalWrite(LED_BUILTIN, HIGH);
            delay(2000);
            analogWrite(FIRST_PWM_PIN+i, 0);
            digitalWrite(LED_BUILTIN, LOW);
            delay(100);
        }
    }

    if(0)
    {
        // alternate strong on 1 for x0 sec then 2 off
        Serial.println("x0 and 2");
        for(int i = 0; i <3; ++i )
        {
            Serial.println("x0");
            analogWrite(FIRST_PWM_PIN, 255);
            digitalWrite(LED_BUILTIN, HIGH);
            delay(60000);
            Serial.println("2");
            analogWrite(FIRST_PWM_PIN+i, 0);
            digitalWrite(LED_BUILTIN, LOW);
            delay(2000);
        }
    }

}

// You can't define the three of them
//#define MEGA
#define PRO_MICRO
//#define XIAO_C3


#ifdef MEGA

  // Arduino Mega Case
# define PWM_PIN_1      8
# define PWM_PIN_2      9
# define PWM_PIN_3      10
# define ANALOG_MAX     255

#endif // MEGA

#ifdef PRO_MICRO
# pragma message( "ATTENTION: C'est pour le PRO_MICRO qu'on compile!" )

  // ou aussi Arduino Pro Micro

  // il faut mettre les chiffres qui sont en bleus sur le schema de ma doc (en bleu c'est le numero "Arduino", la 6 c'est la A7, la 9 c'est la A9 et la 10 c'est la A10 sur le plan)
# define PWM_PIN_1      6 // attention si on met A6 et qu'on le branche sur le 6 ca fonctionne mais pas en analogique (plusieurs chiffres pour une meme sortie mais qui active des modes differents)
# define PWM_PIN_2      9
# define PWM_PIN_3      10
# define ANALOG_MAX     255

#endif // PRO_MICRO

#ifdef XIAO_C3

// ca a fonctionne une fois et puis plus apres, mais pourtant ca semble bon

# pragma message( "ATTENTION: C'est pour le XIAO qu'on compile!" )

# define PWM_PIN_1      2 // A0 is the GPIO 2, so put 2.
# define PWM_PIN_2      3
# define PWM_PIN_3      4
# define LED_BUILTIN    8 // On dirait que le C3 n'a pas de led builtins...
//# define ANALOG_MAX     4095 // it's 12 bits
# define ANALOG_MAX     255 // if it's 8 bits // le probleme on dirait que c'est plutot que ca sort en 3.3V et donc ca envoie pas toute la puissance ?
#endif // XIAO_C3

// Non linear Ramping: input between 0 and 255, same output
// but inputing 128 return around 60
unsigned char nonlinear_ramp(unsigned char input) 
{
  double gamma = 2.4;  // Exposant, adjusted so the value 128 gives ~60
  double normalized_input = input / 255.0;
  double output = 255.0 * pow(normalized_input, gamma);
  return (unsigned char)(output + 0.5); // arrondi
}

int pin_output[] = {PWM_PIN_1,PWM_PIN_2,PWM_PIN_3};

void setup()
{
    Serial.begin( 57600 );

    Serial.println( "INF: MOS Cmd v0.4" );

    pinMode( LED_BUILTIN, OUTPUT );

    for( int j = 0; j < 3; ++j  )
    {
      pinMode( pin_output[j], OUTPUT );
    }
#ifdef XIAO_C3
    analogWriteResolution(8); // force PWM to use 8 bits resolution (NOT TESTED)
#endif

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

    if( 1 )
    {
      Serial.println("full on every of them (digital) !");
      for( int j = 0; j < 3; ++j  )
      {
        digitalWrite( LED_BUILTIN, HIGH );
        digitalWrite( pin_output[j], HIGH );
      }
      delay(3000);
    }
    
    if( 1 )
    {
      Serial.println("full on every of them");
      for( int j = 0; j < 3; ++j  )
      {
        digitalWrite( LED_BUILTIN, HIGH );
        analogWrite( pin_output[j], ANALOG_MAX );
      }
      delay(3000);
      // turn them off
      for( int j = 0; j < 3; ++j  )
      {
        digitalWrite( LED_BUILTIN, LOW );
        analogWrite( pin_output[j], 0 );
      }
    }

    if( 0 )
    {
      // alternate strong and unstrong
      Serial.println("full");
      analogWrite( PWM_PIN_1, 255 );
      digitalWrite( LED_BUILTIN, HIGH );
      delay(5000);
      Serial.println("quarter");
      analogWrite( PWM_PIN_1, 60 );
      delay(5000);
      Serial.println("off");
      analogWrite( PWM_PIN_1, 0 );
      digitalWrite( LED_BUILTIN, LOW );
      delay(5000);
    }

    if(0)
    {
        Serial.println("ramping...");
        for( int i = 0; i < 256; ++i  )
        {
          analogWrite( PWM_PIN_1, i );
          delay(40); // total: 10 sec
        }
    }

    if(0)
    {
        Serial.println("non linear ramping...");
        for( int i = 0; i < 256; ++i  )
        {
          analogWrite( PWM_PIN_1, nonlinear_ramp(i) );
          delay(40); // total: 10 sec
        }
    }

    if(1)
    {
        Serial.println("non linear ramping and unramping on 3...");
        for( int j = 0; j < 3; ++j  )
        {
          Serial.print("ramping on: ");
          Serial.println( pin_output[j] );
          for( int i = 0; i < ANALOG_MAX; ++i  )
          {
            analogWrite( pin_output[j], nonlinear_ramp(i) );
            delay(10); // total: 5 sec
          }
          delay(2000);
          for( int i = ANALOG_MAX; i > 0; --i  )
          {
            analogWrite( pin_output[j], nonlinear_ramp(i) );
            delay(10); // total: 10 sec
          }
        }
    }

    if(0)
    {
        Serial.println("slow ramping...");
        analogWrite(9, 0);
        delay(500);
        for( int i = 0; i < 50; ++i  )
        {
          analogWrite( PWM_PIN_1, i );
          delay(200); // total: 10 sec
        }
    }

    if(0)
    {
        Serial.println("very slow ramping...");
        analogWrite(9, 0);
        delay(500);
        for( int i = 0; i < 20; ++i  )
        {
          analogWrite( PWM_PIN_1, i );
          delay(1000); // total: 20 sec
        }
    }
  
    if(0)
    {
        // alternate strong on every of three
        Serial.println("alternate 3");
        for( int i = 0; i < 3; ++i  )
        {
          Serial.println(i);
          analogWrite( PWM_PIN_1+i, 255 );
          digitalWrite( LED_BUILTIN, HIGH );
          delay(2000);
          analogWrite( PWM_PIN_1+i, 0 );
          digitalWrite( LED_BUILTIN, LOW );
          delay(100);
        }
    }

    if(0)
    {
        // alternate strong on heater number 1 for x0 sec (eg 60sec), then 2 off
        Serial.println("x0 and 2");
        for( int i = 0; i < 3; ++i  )
        {
          Serial.println("x0");
          analogWrite( PWM_PIN_1, 255 );
          digitalWrite( LED_BUILTIN, HIGH );
          delay(60000);
          Serial.println("2");
          analogWrite( PWM_PIN_1+i, 0 );
          digitalWrite( LED_BUILTIN, LOW );
          delay(2000);
        }
    }

}
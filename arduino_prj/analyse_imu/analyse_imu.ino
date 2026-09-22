/*
 
 Plaquer l'imu contre quasi le teton, cable vers le bas, indication IMU contre le torse.



*/

#include <Wire.h>

#define MPU6886_ADDR 0x68

#define REG_WHO_AM_I    0x75
#define REG_PWR_MGMT_1  0x6B
#define REG_ACCEL_XOUT  0x3B

// ============================================================
// Variables
// ============================================================

float gyroBiasX = 0;
float gyroBiasY = 0;
float gyroBiasZ = 0;

float pitch = 0;
float roll  = 0;
float yaw   = 0;

unsigned long lastTime;

int displayCounter = 0;


// ============================================================
// Lecture d'un registre
// ============================================================

uint8_t readRegister(uint8_t reg)
{
  Wire.beginTransmission(MPU6886_ADDR);
  Wire.write(reg);

  if (Wire.endTransmission(false) != 0)
    return 0xFF;

  Wire.requestFrom(MPU6886_ADDR, (uint8_t)1);

  if (Wire.available())
    return Wire.read();

  return 0xFF;
}


// ============================================================
// Lecture de plusieurs registres
// ============================================================

bool readRegisters(uint8_t reg, uint8_t *buffer, uint8_t length)
{
  Wire.beginTransmission(MPU6886_ADDR);
  Wire.write(reg);

  if (Wire.endTransmission(false) != 0)
    return false;

  uint8_t received = Wire.requestFrom(MPU6886_ADDR, length);

  if (received != length)
    return false;

  for (uint8_t i = 0; i < length; i++)
    buffer[i] = Wire.read();

  return true;
}


// ============================================================
// Initialisation MPU6886
// ============================================================

bool initMPU6886()
{
  uint8_t whoami = readRegister(REG_WHO_AM_I);

  Serial.print("WHO_AM_I = 0x");
  Serial.println(whoami, HEX);

  if (whoami != 0x19)
  {
    Serial.println("MPU6886 non detecte !");
    return false;
  }

  // Réveil du MPU
  Wire.beginTransmission(MPU6886_ADDR);
  Wire.write(REG_PWR_MGMT_1);
  Wire.write(0x00);
  Wire.endTransmission();

  delay(100);

  Serial.println("MPU6886 OK");

  return true;
}


// ============================================================
// Calibration du gyroscope
// ============================================================

void calibrateGyro()
{
  Serial.println();
  Serial.println("=================================");
  Serial.println("Calibration gyroscope...");
  Serial.println("NE PAS BOUGER LE MPU6886 !");
  Serial.println("=================================");

  const int samples = 1000;

  float sumX = 0;
  float sumY = 0;
  float sumZ = 0;

  uint8_t data[14];

  for (int i = 0; i < samples; i++)
  {
    if (readRegisters(REG_ACCEL_XOUT, data, 14))
    {
      int16_t gx = ((int16_t)data[8]  << 8) | data[9];
      int16_t gy = ((int16_t)data[10] << 8) | data[11];
      int16_t gz = ((int16_t)data[12] << 8) | data[13];

      sumX += gx / 131.0;
      sumY += gy / 131.0;
      sumZ += gz / 131.0;
    }

    delay(3);
  }

  gyroBiasX = sumX / samples;
  gyroBiasY = sumY / samples;
  gyroBiasZ = sumZ / samples;

  Serial.println();

  Serial.print("Gyro bias X = ");
  Serial.println(gyroBiasX, 4);

  Serial.print("Gyro bias Y = ");
  Serial.println(gyroBiasY, 4);

  Serial.print("Gyro bias Z = ");
  Serial.println(gyroBiasZ, 4);

  Serial.println("Calibration terminee.");
}


// ============================================================
// Lecture complète de l'IMU
// ============================================================

bool readIMU(
  float &ax,
  float &ay,
  float &az,
  float &gx,
  float &gy,
  float &gz,
  float &temperature
)
{
  uint8_t data[14];

  if (!readRegisters(REG_ACCEL_XOUT, data, 14))
    return false;

  int16_t rawAx = ((int16_t)data[0]  << 8) | data[1];
  int16_t rawAy = ((int16_t)data[2]  << 8) | data[3];
  int16_t rawAz = ((int16_t)data[4]  << 8) | data[5];

  int16_t rawTemp = ((int16_t)data[6] << 8) | data[7];

  int16_t rawGx = ((int16_t)data[8]  << 8) | data[9];
  int16_t rawGy = ((int16_t)data[10] << 8) | data[11];
  int16_t rawGz = ((int16_t)data[12] << 8) | data[13];


  // ----------------------------------------------------------
  // Accéléromètre
  // ±2 g = 16384 LSB/g
  // ----------------------------------------------------------

  ax = rawAx / 16384.0;
  ay = rawAy / 16384.0;
  az = rawAz / 16384.0;


  // ----------------------------------------------------------
  // Gyroscope
  // ±250 deg/s = 131 LSB/(deg/s)
  // ----------------------------------------------------------

  gx = rawGx / 131.0;
  gy = rawGy / 131.0;
  gz = rawGz / 131.0;


  // ----------------------------------------------------------
  // Température
  // ----------------------------------------------------------

  temperature = rawTemp / 326.8 + 25.0;

  return true;
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
  Serial.begin(115200);

  Wire.begin();

  // I2C à 400 kHz
  Wire.setClock(400000);

  delay(500);

  Serial.println();
  Serial.println("=================================");
  Serial.println(" MPU6886 - Pitch / Roll / Yaw");
  Serial.println("=================================");

  if (!initMPU6886())
  {
    while (1)
    {
      delay(1000);
    }
  }


  // ----------------------------------------------------------
  // Calibration gyro
  // ----------------------------------------------------------

  calibrateGyro();


  // ----------------------------------------------------------
  // Initialisation des angles avec l'accéléromètre
  // ----------------------------------------------------------

  float ax, ay, az;
  float gx, gy, gz;
  float temperature;

  if (readIMU(ax, ay, az, gx, gy, gz, temperature))
  {
    roll =
      atan2(ay, az) * 180.0 / PI;

    pitch =
      atan2(
        -ax,
        sqrt(ay * ay + az * az)
      ) * 180.0 / PI;

    yaw = 0;
  }


  lastTime = micros();

  Serial.println();
  Serial.println("Orientation initiale OK.");
  Serial.println();
}


float dernierCreux = 0;
float dernierPic = 0;
float pourcentageRespiration = 0;

float calculerPourcentageRespiration(float roll)
{
  static float precedent = 0;
  static bool monte = true;

  // Détection changement de direction
  if (roll > precedent)
  {
    // On vient de repartir vers le haut : le précédent point
    // était un creux
    if (!monte)
    {
      dernierCreux = precedent;
      monte = true;
    }
  }
  else if (roll < precedent)
  {
    // On vient de repartir vers le bas : le précédent point
    // était un pic
    if (monte)
    {
      dernierPic = precedent;
      monte = false;
    }
  }

  // Calcul entre dernier creux et dernier pic
  float amplitude = dernierPic - dernierCreux;

  if (abs(amplitude) > 0.1)
  {
    pourcentageRespiration = (roll - dernierCreux) / amplitude * 100.0;

    pourcentageRespiration = constrain(pourcentageRespiration, 0, 100);
  }

  precedent = roll;

  return pourcentageRespiration;
}

// ============================================================
// Détection respiration à partir du ROLL
// ============================================================

struct RespirationState {
  float filteredRoll = 0;
  float previousRoll = 0;

  float minRoll = 0;
  float maxRoll = 0;

  bool initialized = false;
  bool rising = false;

  float percent = 0;

  unsigned long lastPeakTime = 0;
  unsigned long lastValleyTime = 0;
};

RespirationState resp;


// Paramètres à ajuster
const float RESP_FILTER = 0.15;      // filtrage roll (0.05 = très filtré)
const float RESP_THRESHOLD = 0.015;  // seuil de mouvement
const float RESP_MIN_AMPLITUDE = 2.0; // amplitude minimale en degrés
const unsigned long RESP_MIN_PERIOD = 800; // ms


float updateRespiration(float roll, float gyroX, float gyroY, float gyroZ, float dt)
{
  // ------------------------------------------------------------
  // 1. Filtre passe-bas sur le roll
  // ------------------------------------------------------------
  if (!resp.initialized) {
    resp.filteredRoll = roll;
    resp.previousRoll = roll;
    resp.minRoll = roll;
    resp.maxRoll = roll;
    resp.initialized = true;
    return 50.0;
  }

  resp.filteredRoll += RESP_FILTER * (roll - resp.filteredRoll);


  // ------------------------------------------------------------
  // 2. Vitesse du roll
  // ------------------------------------------------------------
  float velocity = (resp.filteredRoll - resp.previousRoll) / dt;

  resp.previousRoll = resp.filteredRoll;


  // ------------------------------------------------------------
  // 3. Détection montée / descente
  // ------------------------------------------------------------
  bool newRising = resp.rising;

  if (velocity > RESP_THRESHOLD) {
    newRising = true;
  }
  else if (velocity < -RESP_THRESHOLD) {
    newRising = false;
  }


  // ------------------------------------------------------------
  // 4. Changement montée -> descente = PIC
  // ------------------------------------------------------------
  if (resp.rising && !newRising) {

    float amplitude = resp.maxRoll - resp.minRoll;

    if (amplitude >= RESP_MIN_AMPLITUDE) {

      unsigned long now = millis();

      if (now - resp.lastPeakTime > RESP_MIN_PERIOD) {

        resp.maxRoll = resp.filteredRoll;

        Serial.print(">>> FIN INSPIRATION / PIC   roll=");
        Serial.println(resp.filteredRoll, 2);

        resp.lastPeakTime = now;
      }
    }
  }


  // ------------------------------------------------------------
  // 5. Changement descente -> montée = CREUX
  // ------------------------------------------------------------
  if (!resp.rising && newRising) {

    float amplitude = resp.maxRoll - resp.minRoll;

    if (amplitude >= RESP_MIN_AMPLITUDE) {

      unsigned long now = millis();

      if (now - resp.lastValleyTime > RESP_MIN_PERIOD) {

        resp.minRoll = resp.filteredRoll;

        Serial.print(">>> FIN EXPIRATION / CREUX   roll=");
        Serial.println(resp.filteredRoll, 2);

        resp.lastValleyTime = now;
      }
    }
  }


  resp.rising = newRising;


  // ------------------------------------------------------------
  // 6. Mise à jour des extrêmes
  // ------------------------------------------------------------

  if (resp.filteredRoll > resp.maxRoll)
    resp.maxRoll = resp.filteredRoll;

  if (resp.filteredRoll < resp.minRoll)
    resp.minRoll = resp.filteredRoll;


  // ------------------------------------------------------------
  // 7. Pourcentage respiration
  // ------------------------------------------------------------

  float amplitude = resp.maxRoll - resp.minRoll;

  if (amplitude > RESP_MIN_AMPLITUDE) {

    resp.percent =
      100.0 * (resp.filteredRoll - resp.minRoll) / amplitude;

    resp.percent = constrain(resp.percent, 0, 100);
  }


  return resp.percent;
}


float computeRespi( float roll )
{
  // version faite a la mimine.

  static float respmin = +1000;
  static float respmax = -1000;
  static int   countup = 0;
  static int   countdown = 0;

  static int   lastmaxcountup = 0;
  static int   lastmaxcountdown = 0;

  static float   lastmaxrollavg = 0;
  static float   lastminrollavg = 0;

  static float   maxrollavg = 0;
  static float   minrollavg = 0;

  static float rollavg = 0;

  const float coefnew = 0.1;

  const char * state = "";

  rollavg = roll * coefnew + rollavg * (1-coefnew);

  int inccountdown = 0;
  int inccountup = 0;

  const float margin = 0.04;

  if( rollavg > roll + margin )
  {
    ++countdown;
    inccountdown = 1;
  }
  if( rollavg < roll - margin )
  {
    ++countup;
    inccountup = 1;
  }

  if( maxrollavg < rollavg )
  {
    maxrollavg = rollavg;
  }
  if( minrollavg > rollavg )
  {
    minrollavg = rollavg;
  }

  if( inccountdown && countdown > 5 )
  {
    lastmaxcountup = countup;
    if( countup > 0)
    {
      countup = 0;
      lastminrollavg = minrollavg;
      minrollavg = 2000;
      state = "UP";
    }
  }
  if( inccountup && countup > 5 )
  {
    lastmaxcountdown = countdown;
    if( countdown > 0)
    {
      countdown = 0;
      lastmaxrollavg = maxrollavg;
      maxrollavg = -2000;
      state = "DOWN";
    }
  }


  float ratio_respi = (rollavg - lastminrollavg ) / (lastmaxrollavg-lastminrollavg);
  ratio_respi = 1 - ratio_respi;

  ratio_respi = constrain( ratio_respi, 0, 1);

  if( 1 )
  {
    Serial.print( "roll: " );
    Serial.print( roll );

    Serial.print( ", rollavg: " );
    Serial.print( rollavg );

    Serial.print( ", countdown: " );
    Serial.print( countdown );
    Serial.print( ", countup: " );
    Serial.print( countup );

    Serial.print( ", lastminrollavg: " );
    Serial.print( lastminrollavg );
    Serial.print( ", lastmaxrollavg: " );
    Serial.print( lastmaxrollavg );

    Serial.print( ", ratio_respi: " );
    Serial.print( ratio_respi );


    Serial.print( ", " );
    
  /*
    if( rollavg < respmin )
    {
      respmin = roll;
      Serial.print( "min");
    }
    if( rollavg > respmax )
    {
      respmax = roll;
      Serial.print( "max");
    }
    */

    Serial.println( state );
  }

  if( 0 )
  {
    // pour tracer la courbe

    Serial.print( "ratio_respi:" ); // ne pas mettre d'espace apres les :
    Serial.print( ratio_respi );

    // empeche l'autozoom
    Serial.print("\tMIN:");
    Serial.print(0);

    Serial.print("\tMAX:");
    Serial.println(1);
  }


}


// ============================================================
// LOOP
// ============================================================

void loop()
{
  float ax, ay, az;
  float gx, gy, gz;
  float temperature;


  // ----------------------------------------------------------
  // Lecture IMU
  // ----------------------------------------------------------

  if (!readIMU(
        ax,
        ay,
        az,
        gx,
        gy,
        gz,
        temperature))
  {
    Serial.println("Erreur lecture MPU6886");
    delay(10);
    return;
  }


  // ----------------------------------------------------------
  // Calcul du vrai dt
  // ----------------------------------------------------------

  unsigned long now = micros();

  float dt = (now - lastTime) / 1000000.0;

  lastTime = now;


  // Sécurité
  if (dt <= 0 || dt > 0.1)
    dt = 0.01;


  // ----------------------------------------------------------
  // Retrait du bias gyro
  // ----------------------------------------------------------

  gx -= gyroBiasX;
  gy -= gyroBiasY;
  gz -= gyroBiasZ;


  // ----------------------------------------------------------
  // Angles provenant de l'accéléromètre
  // ----------------------------------------------------------

  float accelRoll =
    atan2(ay, az) * 180.0 / PI;

  float accelPitch =
    atan2(
      -ax,
      sqrt(ay * ay + az * az)
    ) * 180.0 / PI;


  // ----------------------------------------------------------
  // Intégration du gyroscope
  // ----------------------------------------------------------

  float gyroRoll =
    roll + gx * dt;

  float gyroPitch =
    pitch + gy * dt;


  // Yaw = intégration pure du gyro Z
  yaw += gz * dt;


  // ----------------------------------------------------------
  // Filtre complémentaire
  // ----------------------------------------------------------

  const float alpha = 0.98;

  roll =
    alpha * gyroRoll +
    (1.0 - alpha) * accelRoll;

  pitch =
    alpha * gyroPitch +
    (1.0 - alpha) * accelPitch;


  // float pourcentageRespiration = calculerPourcentageRespiration( roll );

  // float respPercent = updateRespiration( roll, gx, gy, gz, dt );

  computeRespi( roll );




  // ----------------------------------------------------------
  // Affichage seulement 1 fois sur 10
  //
  // La lecture et les calculs continuent à ~100 Hz.
  // Seul l'affichage est réduit à ~10 Hz.
  // ----------------------------------------------------------

  displayCounter++;

  if (displayCounter >= 10 && 0)
  {
    displayCounter = 0;

    Serial.print("dt=");
    Serial.print(dt * 1000.0, 2);
    Serial.print(" ms");

    Serial.print(" | Pitch=");
    Serial.print(pitch, 2);
    Serial.print(" deg");

    Serial.print(" | Roll=");
    Serial.print(roll, 2);
    Serial.print(" deg");

    Serial.print(" | Yaw=");
    Serial.print(yaw, 2);
    Serial.print(" deg");

    Serial.print(" | Gyro=");
    Serial.print(gx, 2);
    Serial.print(",");
    Serial.print(gy, 2);
    Serial.print(",");
    Serial.print(gz, 2);

    Serial.print(" | Temp=");
    Serial.print(temperature, 2);
    Serial.print(" C");

    // Serial.print(" | % respi=");
    // Serial.print(pourcentageRespiration, 2);

    //Serial.print(", Respiration = ");
    //Serial.print(respPercent, 1);
    //Serial.print(" %");


    Serial.println("");

  return ;

  }


  // ----------------------------------------------------------
  // ~100 Hz
  // ----------------------------------------------------------

  delay(10);
}
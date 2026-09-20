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


// ============================================================
// Lecture registres
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

  // Sortie du mode sleep
  Wire.beginTransmission(MPU6886_ADDR);
  Wire.write(REG_PWR_MGMT_1);
  Wire.write(0x00);
  Wire.endTransmission();

  delay(100);

  Serial.println("MPU6886 OK");

  return true;
}


// ============================================================
// Calibration gyroscope
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
// Lecture IMU
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


  // Accel ±2g
  ax = rawAx / 16384.0;
  ay = rawAy / 16384.0;
  az = rawAz / 16384.0;


  // Gyro ±250 deg/s
  gx = rawGx / 131.0;
  gy = rawGy / 131.0;
  gz = rawGz / 131.0;


  // Température
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

  // I2C rapide
  Wire.setClock(400000);

  delay(500);

  Serial.println();
  Serial.println("=================================");
  Serial.println(" MPU6886 - Pitch Roll Yaw");
  Serial.println("=================================");

  if (!initMPU6886())
  {
    while (1)
    {
      delay(1000);
    }
  }

  // Calibration gyro
  calibrateGyro();

  // Initialisation des angles avec l'accéléromètre
  float ax, ay, az;
  float gx, gy, gz;
  float temperature;

  if (readIMU(ax, ay, az, gx, gy, gz, temperature))
  {
    roll = atan2(ay, az) * 180.0 / PI;

    pitch = atan2(
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


// ============================================================
// LOOP
// ============================================================

void loop()
{
  float ax, ay, az;
  float gx, gy, gz;
  float temperature;

  if (!readIMU(ax, ay, az, gx, gy, gz, temperature))
  {
    Serial.println("Erreur lecture MPU6886");
    delay(100);
    return;
  }


  // ----------------------------------------------------------
  // Delta temps
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
  // Intégration gyroscope
  // ----------------------------------------------------------

  float gyroRoll  = roll  + gx * dt;
  float gyroPitch = pitch + gy * dt;

  yaw += gz * dt;


  // ----------------------------------------------------------
  // Filtre complémentaire
  //
  // 98% gyro
  // 2% accélération
  //
  // Le gyro donne la dynamique.
  // L'accéléromètre corrige la dérive du pitch/roll.
  // ----------------------------------------------------------

  const float alpha = 0.98;

  roll =
    alpha * gyroRoll +
    (1.0 - alpha) * accelRoll;

  pitch =
    alpha * gyroPitch +
    (1.0 - alpha) * accelPitch;


  // ----------------------------------------------------------
  // Affichage
  // ----------------------------------------------------------

  Serial.print("Pitch: ");
  Serial.print(pitch, 2);

  Serial.print(" deg   Roll: ");
  Serial.print(roll, 2);

  Serial.print(" deg   Yaw: ");
  Serial.print(yaw, 2);

  Serial.println(" deg");


  // Valeurs gyro
  Serial.print("Gyro: ");
  Serial.print(gx, 2);
  Serial.print("  ");
  Serial.print(gy, 2);
  Serial.print("  ");
  Serial.print(gz, 2);

  Serial.print(" deg/s   Temp: ");
  Serial.print(temperature, 2);
  Serial.println(" C");


  delay(10);
}
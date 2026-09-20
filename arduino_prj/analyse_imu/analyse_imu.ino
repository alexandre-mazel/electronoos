#include <Wire.h>

#define MPU6886_ADDR 0x68

// Registres MPU6886
#define REG_WHO_AM_I   0x75
#define REG_PWR_MGMT_1 0x6B
#define REG_ACCEL_XOUT 0x3B
#define REG_GYRO_XOUT  0x43
#define REG_TEMP_OUT   0x41

bool mpuFound = false;
uint8_t mpuAddress = MPU6886_ADDR;


// ------------------------------------------------------------
// Écriture d'un registre
// ------------------------------------------------------------
void writeRegister(uint8_t reg, uint8_t value)
{
  Wire.beginTransmission(mpuAddress);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}


// ------------------------------------------------------------
// Lecture d'un registre
// ------------------------------------------------------------
uint8_t readRegister(uint8_t reg)
{
  Wire.beginTransmission(mpuAddress);
  Wire.write(reg);

  if (Wire.endTransmission(false) != 0)
    return 0xFF;

  Wire.requestFrom(mpuAddress, (uint8_t)1);

  if (Wire.available())
    return Wire.read();

  return 0xFF;
}


// ------------------------------------------------------------
// Lecture de plusieurs octets
// ------------------------------------------------------------
bool readRegisters(uint8_t reg, uint8_t *buffer, uint8_t length)
{
  Wire.beginTransmission(mpuAddress);
  Wire.write(reg);

  if (Wire.endTransmission(false) != 0)
    return false;

  uint8_t received = Wire.requestFrom(mpuAddress, length);

  if (received != length)
    return false;

  for (uint8_t i = 0; i < length; i++)
    buffer[i] = Wire.read();

  return true;
}


// ------------------------------------------------------------
// Scan I2C
// ------------------------------------------------------------
void scanI2C()
{
  Serial.println();
  Serial.println(F("========== SCAN I2C =========="));

  int devices = 0;

  for (uint8_t address = 1; address < 127; address++)
  {
    Wire.beginTransmission(address);

    uint8_t error = Wire.endTransmission();

    if (error == 0)
    {
      Serial.print(F("I2C device trouve : 0x"));

      if (address < 16)
        Serial.print('0');

      Serial.println(address, HEX);

      devices++;

      // On mémorise le MPU si trouvé
      if (address == 0x68 || address == 0x69)
      {
        mpuAddress = address;
        mpuFound = true;
      }
    }
  }

  if (devices == 0)
    Serial.println(F("Aucun device I2C trouve."));

  Serial.print(F("Nombre de devices : "));
  Serial.println(devices);

  Serial.println(F("=============================="));
}


// ------------------------------------------------------------
// Initialisation MPU6886
// ------------------------------------------------------------
bool initMPU6886()
{
  uint8_t whoami = readRegister(REG_WHO_AM_I);

  Serial.print(F("WHO_AM_I = 0x"));

  if (whoami < 16)
    Serial.print('0');

  Serial.println(whoami, HEX);

  // Le MPU6886 retourne normalement 0x19
  if (whoami != 0x19)
  {
    Serial.println(F("ATTENTION : WHO_AM_I != 0x19"));
    return false;
  }

  // Réveil
  writeRegister(REG_PWR_MGMT_1, 0x00);

  delay(100);

  Serial.println(F("MPU6886 initialise."));

  return true;
}


// ------------------------------------------------------------
// Lecture IMU
// ------------------------------------------------------------
void readMPU6886()
{
  uint8_t data[14];

  /*
    14 octets :

    0-1   ACCEL X
    2-3   ACCEL Y
    4-5   ACCEL Z
    6-7   TEMP
    8-9   GYRO X
    10-11 GYRO Y
    12-13 GYRO Z
  */

  if (!readRegisters(REG_ACCEL_XOUT, data, 14))
  {
    Serial.println(F("Erreur lecture MPU6886"));
    return;
  }

  int16_t ax = ((int16_t)data[0] << 8) | data[1];
  int16_t ay = ((int16_t)data[2] << 8) | data[3];
  int16_t az = ((int16_t)data[4] << 8) | data[5];

  int16_t temp = ((int16_t)data[6] << 8) | data[7];

  int16_t gx = ((int16_t)data[8] << 8) | data[9];
  int16_t gy = ((int16_t)data[10] << 8) | data[11];
  int16_t gz = ((int16_t)data[12] << 8) | data[13];


  // ----------------------------------------------------------
  // Conversion
  //
  // Configuration par défaut :
  // Accel ±2g  -> 16384 LSB/g
  // Gyro ±250°/s -> 131 LSB/(°/s)
  // ----------------------------------------------------------

  float ax_g = ax / 16384.0;
  float ay_g = ay / 16384.0;
  float az_g = az / 16384.0;

  float gx_dps = gx / 131.0;
  float gy_dps = gy / 131.0;
  float gz_dps = gz / 131.0;

  // Température MPU
  float temperature = temp / 326.8 + 25.0;


  // ----------------------------------------------------------
  // Affichage
  // ----------------------------------------------------------

  Serial.println();
  Serial.println(F("------------- MPU6886 -------------"));

  Serial.print(F("ACC raw : "));
  Serial.print(ax);
  Serial.print(F("  "));
  Serial.print(ay);
  Serial.print(F("  "));
  Serial.println(az);

  Serial.print(F("ACC [g] : "));
  Serial.print(ax_g, 4);
  Serial.print(F("  "));
  Serial.print(ay_g, 4);
  Serial.print(F("  "));
  Serial.println(az_g, 4);


  Serial.print(F("GYRO raw: "));
  Serial.print(gx);
  Serial.print(F("  "));
  Serial.print(gy);
  Serial.print(F("  "));
  Serial.println(gz);

  Serial.print(F("GYRO [deg/s] : "));
  Serial.print(gx_dps, 3);
  Serial.print(F("  "));
  Serial.print(gy_dps, 3);
  Serial.print(F("  "));
  Serial.println(gz_dps, 3);


  Serial.print(F("TEMP raw : "));
  Serial.println(temp);

  Serial.print(F("TEMP [C] : "));
  Serial.println(temperature, 2);

  Serial.println(F("-----------------------------------"));
}


// ------------------------------------------------------------
// SETUP
// ------------------------------------------------------------
void setup()
{
  Serial.begin(115200);

  while (!Serial)
    ;

  Wire.begin();

  // Mega2560 : SDA = 20, SCL = 21
  Wire.setClock(400000);

  Serial.println();
  Serial.println(F("==================================="));
  Serial.println(F(" Arduino Mega 2560 - MPU6886"));
  Serial.println(F("==================================="));

  delay(500);

  scanI2C();

  if (mpuFound)
  {
    Serial.print(F("MPU potentiel trouve a 0x"));

    if (mpuAddress < 16)
      Serial.print('0');

    Serial.println(mpuAddress, HEX);

    if (!initMPU6886())
      Serial.println(F("Echec initialisation MPU6886"));
  }
  else
  {
    Serial.println(F("MPU6886 non trouve."));
  }
}


// ------------------------------------------------------------
// LOOP
// ------------------------------------------------------------
void loop()
{
  // Scan I2C à chaque tour
  //scanI2C();

  // Vérification MPU
  if (mpuFound)
  {
    uint8_t whoami = readRegister(REG_WHO_AM_I);

    Serial.print(F("MPU WHO_AM_I : 0x"));

    if (whoami < 16)
      Serial.print('0');

    Serial.println(whoami, HEX);

    readMPU6886();
  }
  else
  {
    Serial.println(F("Pas de MPU6886 detecte."));
  }

  Serial.println();
  Serial.println(F("==================================="));

  delay(1000);
}

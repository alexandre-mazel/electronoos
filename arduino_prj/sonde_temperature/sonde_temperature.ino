#define DS18B20MODEL 0x28
#include "OneWire.h"
#include "DallasTemperature.h"
 
 /* Broche du bus 1-Wire */
const byte BROCHE_ONEWIRE = 2;

/* Code de retour de la fonction getTemperature() */
enum DS18B20_RCODES {
  READ_OK,  // Lecture ok
  NO_SENSOR_FOUND,  // Pas de capteur
  INVALID_ADDRESS,  // Adresse reçue invalide
  INVALID_SENSOR  // Capteur invalide (pas un DS18B20)
};

//OneWire oneWire(A1);
//OneWire oneWire(10);
OneWire ds(BROCHE_ONEWIRE);

#define USE_DALLAS 1 // avec et sans ca fonctionne, mais avec je peux gerer plusieurs capteurs sur une meme entrée.

#ifdef USE_DALLAS
DallasTemperature sensors(&ds);
#endif

void discoverOneWireDevices(void) {
  byte i;
  byte present = 0;
  byte data[12];
  byte addr[8];
  
  Serial.print("Looking for 1-Wire devices...\n\r");

  while(ds.search(addr)) {
    Serial.print("\n\rFound \'1-Wire\' device with address:\n\r");

    for( i = 0; i < 8; i++) {
      Serial.print("0x");
      if (addr[i] < 16) {
        Serial.print('0');

      }
      Serial.print(addr[i], HEX);
      if (i < 7) {
        Serial.print(", ");

      }
    }
    if ( OneWire::crc8( addr, 7) != addr[7]) {
        Serial.print("CRC is not valid!\n");
        return;
    }
  }
  Serial.print("\n\r\n\rThat's it.\r\n");
  ds.reset_search();
  return;
}

void lookUpSensors(){
  byte address[8];
  int i=0;
  byte ok = 0, tmp = 0;
  //start the search
  Serial.println("--Search started--");
  while (ds.search(address)){
    tmp = 0;
    //0x10 = DS18S20
    if (address[0] == 0x10){
      Serial.print("Device is a DS18S20 : ");
      tmp = 1;
    } else {
      //0x28 = DS18B20
      if (address[0] == 0x28){
        Serial.print("Device is a DS18B20 : ");
        tmp = 1;
      }
    }
    //display the address, if tmp is ok
    if (tmp == 1){
      if (OneWire::crc8(address, 7) != address[7]){
        Serial.println("but it doesn't have a valid CRC!");
      } else {
        //all is ok, display it
        for (i=0;i<8;i++){
          if (address[i] < 9){
            Serial.print("0");
          }
          Serial.print(address[i],HEX);
          if (i<7){
            Serial.print("-");
          }
        }
        Serial.println("");
        ok = 1;
      }
    }//end if tmp
  }//end while
  if (ok == 0){
    Serial.println("No devices were found");
  }
  Serial.println("--Search ended--");
}

void setup() {
  Serial.begin(9600);  // definition de l'ouverture du port serie
  pinMode(BROCHE_ONEWIRE,INPUT);

#ifdef USE_DALLAS
  Serial.println("using Dallas");
  sensors.begin();          // sonde activee
#else
  lookUpSensors();
  //discoverOneWireDevices();
#endif

}

/**
 * Fonction de lecture de la température via un capteur DS18B20.
 */
byte getTemperature(float *temperature, byte reset_search) {
  byte data[9], addr[8];
  // data[] : Données lues depuis le scratchpad
  // addr[] : Adresse du module 1-Wire détecté
  
  /* Reset le bus 1-Wire si nécessaire (requis pour la lecture du premier capteur) */
  if (reset_search) {
    //Serial.println("INF: getTemperature: resetting..." );
    ds.reset_search();
  }
 
  /* Recherche le prochain capteur 1-Wire disponible */
  if (!ds.search(addr)) {
    // Pas de capteur
    Serial.println("ERR: getTemperature: NO_SENSOR_FOUND" );
    return NO_SENSOR_FOUND;
  }

#if 0
  Serial.print("DBG: addr: ");

  for(int i = 0; i < 9; i++)
    Serial.print(addr[i]);
  Serial.println("");
#endif

  /* Vérifie que l'adresse a été correctement reçue */
  if (OneWire::crc8(addr, 7) != addr[7]) {
    // Adresse invalide
    Serial.println("ERR: getTemperature: INVALID_ADDRESS" );
    return INVALID_ADDRESS;
  }
 
  /* Vérifie qu'il s'agit bien d'un DS18B20 */
  if (addr[0] != 0x28) {
    // Mauvais type de capteur
    Serial.println("ERR: getTemperature: INVALID_SENSOR" );
    return INVALID_SENSOR;
  }
 
  /* Reset le bus 1-Wire et sélectionne le capteur */
  ds.reset();
  ds.select(addr);
  
  /* Lance une prise de mesure de température et attend la fin de la mesure */
  ds.write(0x44, 1);
  delay(800);
  
  /* Reset le bus 1-Wire, sélectionne le capteur et envoie une demande de lecture du scratchpad */
  ds.reset();
  ds.select(addr);
  ds.write(0xBE);
 
 /* Lecture du scratchpad */
  for (byte i = 0; i < 9; i++) {
    data[i] = ds.read();
  }
   
  /* Calcul de la température en degré Celsius */
  *temperature = (int16_t) ((data[1] << 8) | data[0]) * 0.0625; 
  
  // Pas d'erreur
  return READ_OK;
}

void loop() {
#if USE_DALLAS

  sensors.requestTemperatures();
  for( int i = 0; i < 5; ++i)
  {
    float t = sensors.getTempCByIndex(i);
    if( t <= -40 ) break;
    Serial.print(i);
    Serial.print(": ");
    Serial.print(t,1);
    Serial.println( "C" );
  }
  delay(1000);

#else
  if( 1)
  {
    delay(1000);
    float temperature;
    
    /* Lit la température ambiante à ~1Hz */
    if (getTemperature(&temperature, true) != READ_OK) {
      Serial.println(F("Erreur de lecture du capteur"));
      return;
    }

    /* Affiche la température */
    Serial.print(F("Temperature : "));
    Serial.print(temperature, 1);
    //Serial.write(176); // Caractère degré
    //Serial.write('C');
    Serial.write('deg');
    Serial.println();
  }
  else
  {
    int v;
    //v =  analogRead(A1);
    v =  analogRead(MISO);
    Serial.println( v );
    delay(10);
  }
#endif // else DALLAS

}
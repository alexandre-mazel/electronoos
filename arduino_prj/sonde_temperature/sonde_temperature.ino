#include "OneWire.h"
#include "DallasTemperature.h"
 
 /* Broche du bus 1-Wire */
const byte BROCHE_ONEWIRE = 10;

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

//DallasTemperature ds(&oneWire);


void setup() {
  Serial.begin(9600);  // definition de l'ouverture du port serie
  //ds.begin();          // sonde activee
}

/**
 * Fonction de lecture de la température via un capteur DS18B20.
 */
byte getTemperature(float *temperature, byte reset_search) {
  byte data[9], addr[8];
  // data[] : Données lues depuis le scratchpad
  // addr[] : Adresse du module 1-Wire détecté
  
  /* Reset le bus 1-Wire ci nécessaire (requis pour la lecture du premier capteur) */
  if (reset_search) {
    ds.reset_search();
  }
 
  /* Recherche le prochain capteur 1-Wire disponible */
  if (!ds.search(addr)) {
    // Pas de capteur
    return NO_SENSOR_FOUND;
  }
  
  /* Vérifie que l'adresse a été correctement reçue */
  if (OneWire::crc8(addr, 7) != addr[7]) {
    // Adresse invalide
    return INVALID_ADDRESS;
  }
 
  /* Vérifie qu'il s'agit bien d'un DS18B20 */
  if (addr[0] != 0x28) {
    // Mauvais type de capteur
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
  if( 0 )
  {
    //ds.requestTemperatures();
    //int t = ds.getTempCByIndex(0);
    //Serial.print(t);
    Serial.println( "C" );
    delay(1000);
  }
  else if( 1)
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
    Serial.print(temperature, 2);
    Serial.write(176); // Caractère degré
    Serial.write('C');
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

}
/*
 * La table des Aromes des Caves du Louvre
 * 
 * Version number: cf the message in the print of the setup function
 * Author: Alexandre Mazel
 * copyright (c) A.Mazel 2015
 */
 
 #include <EEPROM.h>
 
int pEprom = 0;
 
byte nNbrBoot;
 
 void setup()
{
  Serial.begin(9600);
  Serial.println("Test...");
  
  nNbrBoot = EEPROM.read(pEprom);
  Serial.write( "Boot: " );
  Serial.print( nNbrBoot, DEC );  
  ++nNbrBoot;
  EEPROM.write(pEprom, nNbrBoot);
  
}
 
void loop()
{

}

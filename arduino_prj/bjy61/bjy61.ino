int incomingByte = 0;   // for incoming serial data

void setup() {
  
        Serial.begin(9600);
        Serial.print("DBG: Opening port...");
        Serial3.begin(115200);
        Serial.print("DBG: Open...");        
}

void analyse(signed short)
{
  // it looks like (in hex, for acceleration) 55 51 ax_lo ax_hi ay_lo ay_hi az_lo az_hi temp_lo temp_hi checksum; 55 52 and 55 53 are headers for angular velocity and total angle, respectively.
  
}

void loop() {

        // send data only when you receive data:
        if (Serial3.available() > 0) {
                // read the incoming byte:
                incomingByte = Serial3.read();
                analyse

                // say what you got:
                Serial.print("I received: ");
                Serial.println(incomingByte, DEC);
        }
}

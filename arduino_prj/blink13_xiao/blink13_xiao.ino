void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("blink 13 xiao: loop debug xiao");
  pinMode( LED_BUILTIN, OUTPUT );

}

void loop() {
  // put your main code here, to run repeatedly:
  
  Serial.println("on");
  digitalWrite( LED_BUILTIN, HIGH );
  delay(1000);
  Serial.println("off");
  digitalWrite( LED_BUILTIN, LOW );
  delay(1000);
}

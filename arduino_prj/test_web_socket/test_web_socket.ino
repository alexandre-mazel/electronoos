/*********
  Rui Santos + A.Mazel
  Complete project details at https://RandomNerdTutorials.com/esp32-websocket-server-arduino/
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  // To test this:
  // open http://192.168.0.9:8000/ from a browser (with the esp32 IP)
*********/

// Import required libraries
#include <WiFi.h>
#include <AsyncTCP.h> // install AsyncTCP by ESP32Async
#include <ESPAsyncWebServer.h>

#include "wifi_network.hpp" // lien symbolique vers le hpp ( creer en lancant un cmd en mode administrateur et la commande: ../generate_link_misbkit_prj.bat
#include "misbkit.hpp"
#include "dynamixel_motor.hpp"
#include "debug_lcd.hpp"

// Replace with your network credentials
const char* my_ssid = "Liberte";
const char* my_password = "lagrosseliberte666!";


bool ledState = 0;
const int ledPin = 13;

// Create AsyncWebServer object on port 80
AsyncWebServer server(8000);
AsyncWebSocket ws("/ws");

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP Web Server</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
  html {
    font-family: Arial, Helvetica, sans-serif;
    text-align: center;
  }
  h1 {
    font-size: 1.8rem;
    color: white;
  }
  h2{
    font-size: 1.5rem;
    font-weight: bold;
    color: #143642;
  }
  .topnav {
    overflow: hidden;
    background-color: #143642;
  }
  body {
    margin: 0;
  }
  .content {
    padding: 30px;
    max-width: 600px;
    margin: 0 auto;
  }
  .card {
    background-color: #F8F7F9;;
    box-shadow: 2px 2px 12px 1px rgba(140,140,140,.5);
    padding-top:10px;
    padding-bottom:20px;
  }
  .button {
    padding: 15px 50px;
    font-size: 24px;
    text-align: center;
    outline: none;
    color: #fff;
    background-color: #0f8b8d;
    border: none;
    border-radius: 5px;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    -webkit-tap-highlight-color: rgba(0,0,0,0);
   }
   /*.button:hover {background-color: #0f8b8d}*/
   .button:active {
     background-color: #0f8b8d;
     box-shadow: 2 2px #CDCDCD;
     transform: translateY(2px);
   }
   .state {
     font-size: 1.5rem;
     color:#8c8c8c;
     font-weight: bold;
   }
  </style>
<title>ESP Web Server</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
</head>
<body>
  <div class="topnav">
    <h1>ESP WebSocket Server</h1>
  </div>
  <div class="content">
    <div class="card">
      <h2>Output - GPIO 2</h2>
      <p class="state">state: <span id="state">%STATE%</span></p>
      <p><button id="button" class="button">Toggle</button></p>
    </div>
  </div>
<script>
  var gateway = `ws://${window.location.hostname}:8000/ws`;
  var websocket;
  window.addEventListener('load', onLoad);
  function initWebSocket() {
    console.log('Trying to open a WebSocket connection...');
    websocket = new WebSocket(gateway);
    websocket.onopen    = onOpen;
    websocket.onclose   = onClose;
    websocket.onmessage = onMessage; // <-- add this line
  }
  function onOpen(event) {
    console.log('Connection opened');
  }
  function onClose(event) {
    console.log('Connection closed');
    setTimeout(initWebSocket, 2000);
  }
  function onMessage(event) {
    var state;
    if (event.data == "1"){
      state = "ON";
    }
    else{
      state = "OFF";
    }
    document.getElementById('state').innerHTML = state;
  }
  function onLoad(event) {
    initWebSocket();
    initButton();
  }
  function initButton() {
    document.getElementById('button').addEventListener('click', toggle);
  }
  function toggle(){
    websocket.send('toggle');
  }
</script>
</body>
</html>
)rawliteral";

DyMotors dym;

#define PIN_LED       21 // not installed on our version

#define PIN_BAT       A2 // A4/36 - ADC1

#define PIN_AN_1      A3
#define PIN_AN_2      A9
#define PIN_AN_3      A7

#define PIN_DIGI_1    12 // A8 - ADC2
#define PIN_DIGI_2    27 // A6 - ADC2
#define PIN_DIGI_3    15 // Digital IO

void sensors_init()
{
  pinMode( PIN_LED, OUTPUT );
  pinMode( PIN_BAT, INPUT );

  pinMode( PIN_AN_1, INPUT );
  pinMode( PIN_AN_2, INPUT );
  pinMode( PIN_AN_3, INPUT );

  pinMode( PIN_DIGI_1, INPUT );
  pinMode( PIN_DIGI_2, INPUT );
  pinMode( PIN_DIGI_3, INPUT );
}


void sensors_get( char * buf )
{
  // fill buf with the current sensor state (simulated 10 sensors)
  buf[0] = (uint8_t)analogRead(PIN_AN_1)>>2;
  buf[1] = (uint8_t)analogRead(PIN_AN_2)>>2;
  buf[2] = (uint8_t)analogRead(PIN_AN_3)>>2;

  buf[3] = (uint8_t)digitalRead(PIN_DIGI_1)>>2;
  buf[4] = (uint8_t)digitalRead(PIN_DIGI_2)>>2;
  buf[5] = (uint8_t)digitalRead(PIN_DIGI_3)>>2;

  buf[10] = (uint8_t)analogRead(PIN_BAT)>>2;
}

void notifyClients() {
  ws.textAll(String(ledState));
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    //Serial.print("DBG: handleWebSocketMessage: data: "); Serial.println( (char*)data );
    if (strcmp((char*)data, "toggle") == 0) {
      ledState = !ledState;
      notifyClients();
    }
    if (strncmp((char*)data, "motor",5) == 0) {
      //ledState = !ledState;
      //notifyClients();
      //ws.textAll("1234560123456789B");
      // simulate good order received:
      for(int i = 0; i < 5; ++i )
      {
        dym.sendPosition( i, 100 );
      }
      static char sendpos[] = "PosXXXXXX0123456789B"; // ajout de 10 capteurs et Ã©tat de la batterie
      memcpy( &sendpos[3], (uint8_t*)dym.getAllPositions(), 6 );
      sensors_get(&sendpos[9]);
      static char sendpos_fake[] = "PosXXXXXX0123456789B"; // on ne peut pas recevoir des binaires en WebSocket! => TODO!
      ws.textAll(sendpos_fake);
    }
  }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

String processor(const String& var){
  //Serial.println(var);
  if(var == "STATE"){
    if (ledState){
      return "ON";
    }
    else{
      return "OFF";
    }
  }
  return String();
}

void MotorHandler(AsyncWebServerRequest *request)
{
  static char motors[] = "1234560123456789B";
  Serial.println("DBG: received motors...");
  String message;
   if (request->hasParam("val")) {
      message = request->getParam("val")->value();
   }
  Serial.println("Received message: " + message);
  request->send_P(200, "text/plain", motors );
}

void setup(){
  const char str_version[] = "test_web_socket v0.64";
  Serial.begin(115200);

  Serial.println ( "" );
  Serial.println( str_version );
  setup_lcd( str_version );

  Serial.println ( "" );
  Serial.println( str_version );
  setup_lcd( str_version );

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);
  
  if(0)
  {
    // Connect to Wi-Fi
    Serial.println("Connecting to WiFi..");
    WiFi.begin(my_ssid, my_password);
    while (WiFi.status() != WL_CONNECTED) {
      Serial.print(".");
      delay(1000);
    }
    Serial.println("");
    // Print ESP Local IP Address
    Serial.println(WiFi.localIP());
  }
  else
  {
    createWifiAP( getArduinoId() );
  }

  lcd_print_message( getCurrentIP() );

  initWebSocket();

  sensors_init();
  dym.init();

  // Route for root / web page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send_P(200, "text/html", index_html, processor);
  });

  server.on("/motor", HTTP_GET,MotorHandler ); // Attention: ca c'est le handler html, le WebSocket est plus haut


  // Start server
  server.begin();
  Serial.println( "server started..." );

  lcd_print_message( "Serving on: ", getArduinoId() );
  lcd_print_message( getCurrentIP() );
}

void loop() {
  ws.cleanupClients();
  digitalWrite(ledPin, ledState); // c'est bourrin, a chaque frame on réécris, meme si rien n'a changé!
  delay(10);
}

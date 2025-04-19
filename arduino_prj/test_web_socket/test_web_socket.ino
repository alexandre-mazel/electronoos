/*********
  Rui Santos + A.Mazel
  Complete project details at https://RandomNerdTutorials.com/esp32-websocket-server-arduino/
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  // To test this:
  // open http://192.168.0.9:9000/ from a browser (with the esp32 IP)
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
//const char* my_ssid = "Liberte";
//const char* my_password = "latodo";


bool ledState = 0;
const int ledPin = 13;

// Create AsyncWebServer object on port 80 or 9000
const int nNumPort = 9000;
AsyncWebServer server(nNumPort);
AsyncWebSocket ws("/ws");



const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<!-- Ce/Le fichier copy_of_code* permet de debugger vite fait dans un browser, quand c'est fini on le copie dans le .ino ou il atterira en ram -->
<!-- Si on pouvait l'importer automatiquement depuis le ino, ca serait plus pratique... -->

<head>
  <title>MisBKit Web Server</title>
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
   
input[type=range][orient=vertical] {
    writing-mode: vertical-lr;
    direction: rtl;
    appearance: slider-vertical;
    width: 16px;
    vertical-align: bottom;
    height: 410px;
}

.sensor_div{
height:30px;display: flex;margin: auto;
width:30%% ;  /* pb with percentage sign so leave one space after the sign, so we can change it or not" */
}

.squarebox_div{
margin: auto;
}

.squarebox {
  height: 20px;
  width: 20px;
  margin-bottom: 15px;
  margin: auto;
  background-color:grey;
  border-radius:3px;
}

.sensor_val_div{
width:80%% ;
}

.sensor_val_p{
text-align: left;margin: auto;padding:6px;
}
  </style>
<title>ESP Web Server</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
</head>
<body>
  <div class="topnav">
    <h1>%BOARD_ID% - WebSocket Server</h1>
  </div>
  <div class="content">
    <div class="card">
      <h2>MisBKit Connected: </h2>
      <p id="update_state">?</p>
      <p id="fps">fps: ?</p>
      <p><button id="button_connect" class="button">Reconnect/Disconnect</button></p>
    </div>
  </div>
  <div class="content">
    <div class="card">
      <h2>Internal Led</h2>
      <p class="state">state: <span id="state">%STATE%</span></p>
      <p><button id="button_led" class="button">Toggle</button></p>
    </div>
  </div>

<canvas id="Motor1_graph" width="600" height="400" 
        style="border: 2px solid black"> 
</canvas> 

<input type="range" orient="vertical" id="Motor1_slider" list="steplist" onInput="sliderChange(this.id, 0, this.value)" />
<datalist id="steplist">
    <option>50</option>
</datalist>
<br>

<canvas id="Motor2_graph" width="600" height="400" 
        style="border: 2px solid black"> 
</canvas> 
<input type="range" orient="vertical" id="Motor2_slider" list="steplist" onInput="sliderChange(this.id, 1, this.value)" />
<br>

<canvas id="Motor3_graph" width="600" height="400" 
        style="border: 2px solid black"> 
</canvas> 
<input type="range" orient="vertical" id="Motor3_slider" list="steplist" onInput="sliderChange(this.id, 2, this.value)" />
<br>

<canvas id="Motor4_graph" width="600" height="400" 
        style="border: 2px solid black"> 
</canvas> 
<input type="range" orient="vertical" id="Motor4_slider" list="steplist" onInput="sliderChange(this.id, 3, this.value)" />
<br>

<canvas id="Motor5_graph" width="600" height="400" 
        style="border: 2px solid black"> 
</canvas> 
<input type="range" orient="vertical" id="Motor5_slider" list="steplist" onInput="sliderChange(this.id, 4, this.value)" />
<br>

<canvas id="Motor6_graph" width="600" height="400" 
        style="border: 2px solid black"> 
</canvas> 
<input type="range" orient="vertical" id="Motor6_slider" list="steplist" onInput="sliderChange(this.id, 5, this.value)" />

  <div class="content">
    <div class="card">
      <h2>Sensor </h2>
      <div class = "sensor_div" ><div class='squarebox_div'><div class='squarebox' id="Sens1_box"></div></div><div class="sensor_val_div"><p class="sensor_val_p" id="Sens1_val">Sensor1 value</p></div></div>
      <div class = "sensor_div" ><div class='squarebox_div'><div class='squarebox' id="Sens2_box"></div></div><div class="sensor_val_div"><p class="sensor_val_p" id="Sens2_val">Sensor2 value</p></div></div>
      <div class = "sensor_div" ><div class='squarebox_div'><div class='squarebox' id="Sens3_box"></div></div><div class="sensor_val_div"><p class="sensor_val_p" id="Sens3_val">Sensor3 value</p></div></div>
      <div class = "sensor_div" ><div class='squarebox_div'><div class='squarebox' id="Sens4_box"></div></div><div class="sensor_val_div"><p class="sensor_val_p" id="Sens4_val">Sensor4 value</p></div></div>
      <div class = "sensor_div" ><div class='squarebox_div'><div class='squarebox' id="Sens5_box"></div></div><div class="sensor_val_div"><p class="sensor_val_p" id="Sens5_val">Sensor5 value</p></div></div>
      <div class = "sensor_div" ><div class='squarebox_div'><div class='squarebox' id="Sens6_box"></div></div><div class="sensor_val_div"><p class="sensor_val_p" id="Sens6_val">Sensor6 value</p></div></div>
    </div>
  </div>


<br>

<script>
  var gateway = 'ws://' + window.location.hostname + ':9000/ws';
  var websocket = 0;
  
  var aaPosDevices = [];
  var aTimes = [];
  var nNbrValByDevice = 100;
  var aListCtx = [];
  const nNbrMotorInterface = 6; // nbr motor with graph interface
  const nNbrSensorInterface = 10; // nbr motor with just number
  var aOrderMotor = []; // between -128 to 128
  var no_update_cpt = 0;
  var nbr_update = 0;
  var time_start_cpt_fps = 0;
  
  /**
 * Convert a 12-bit value (0–4095) to a pseudo RGB color.
 * @param {number} value - The 12-bit input value.
 * @returns {{r: number, g: number, b: number}} - An object with RGB components (0–255).
 */
function pseudoColorFrom12Bit(value) {
  // Clamp the input value to the 0–4095 range
  value = Math.max(0, Math.min(4095, value));

  // Normalize to 0–1
  const normalized = value / 4095;

  // Map the normalized value to a pseudo-color using a simple colormap
  // Example: blue (low) -> cyan -> green -> yellow -> red (high)

  let r = 0, g = 0, b = 0;

  if (normalized < 0.25) {
    // Blue to Cyan
    r = 0;
    g = normalized * 4 * 255;
    b = 255;
  } else if (normalized < 0.5) {
    // Cyan to Green
    r = 0;
    g = 255;
    b = (1 - (normalized - 0.25) * 4) * 255;
  } else if (normalized < 0.75) {
    // Green to Yellow
    r = (normalized - 0.5) * 4 * 255;
    g = 255;
    b = 0;
  } else {
    // Yellow to Red
    r = 255;
    g = (1 - (normalized - 0.75) * 4) * 255;
    b = 0;
  }
/*
  return {
    r: Math.round(r),
    g: Math.round(g),
    b: Math.round(b)
  };
  */
  return "rgb("+r+","+g+","+b+")"
}
  
  window.addEventListener('load', onLoad);
  function initWebSocket() {
    if(window.location.hostname == "" )
    {
        console.log('WRN: initWebSocket: localhost detected so no websocket creation...');
        return;
    }
    console.log('DBG: initWebSocket: Trying to open a WebSocket connection...');
    console.log( "gateway: " + gateway );
    websocket = new WebSocket(gateway);
    websocket.onopen    = onOpen;
    websocket.onclose   = onClose;
    websocket.onmessage = onMessage; // <-- add this line
    document.getElementById('button_connect').innerHTML = "Disconnect";
    setTimeout( updateMotorsAndSensors, 1000 );
  }
  function toggleConnect()
  {
    if( websocket != 0 )
    {
        console.log( 'DBG: toggleConnect: disconnecting');
        websocket.close();
        websocket = 0;
        document.getElementById('button_connect').innerHTML = "Reconnect";
    }
    else
    {
        console.log( 'DBG: toggleConnect: reconnecting');
        initWebSocket();
    }
  }
  function onOpen(event) {
    console.log('Connection opened');
  }
  function onClose(event) {
    console.log('Connection closed');
    //setTimeout(initWebSocket, 2000);
  }
  function onMessage(event) {
    var state;
    //console.log( "DBG: onMessage: Data received: ", event.data )
    if (event.data == "1"){
      state = "ON";
      document.getElementById('state').innerHTML = state;
    }
    else if (event.data == "0"){
      state = "OFF";
      document.getElementById('state').innerHTML = state;
    }
    else if (event.data[0] == "P" && event.data[1] == "o" )
    {
        // Message has the style: "Pos_CcAnC3C8CiB.01234567890123456789B"
        let msg = event.data;
        addTimeToVal();
        for (var i = 0; i < nNbrMotorInterface; i++ )
        {
            const start_pos = 4;
            let val = b64_to_sint( msg.substring(start_pos+i*2,start_pos+i*2+2) );
            updateDeviceVal( i, val );
        }
        for (var i = 0; i < nNbrSensorInterface; i++ )
        {
            const start_pos = 4+6*2;
            let val = b64_to_ushint( msg.substring(start_pos+i*2,start_pos+i*2+2) );
            updateSensorVal( i, val );
        }
        // TODO: here: faire clignoter un petit point quelques part pour montrer qu'on est connecté est rafraichi (genre un truc qui s'estompe avec le temps)
        no_update_cpt = 0;
        document.getElementById('update_state').innerHTML = "connected";
        nbr_update += 1;
        if( Date.now() - time_start_cpt_fps > 5*1000 )
        {
            let fps = (nbr_update * 1000) / ( Date.now() - time_start_cpt_fps )
            document.getElementById('fps').innerHTML = "fps: " + fps.toFixed(2);
            time_start_cpt_fps = Date.now();
            nbr_update = 0;
        }
        // prepare a new update send
        setTimeout( updateMotorsAndSensors, 10 );
    } // end Pos received
  }
  function onLoad(event) {
    initWebSocket();
    initButton();
  }
  function initButton() {
    document.getElementById('button_led').addEventListener('click', toggleLed);
    document.getElementById('button_connect').addEventListener('click', toggleConnect);
  }
  function toggleLed(){
    websocket.send('toggle');
  }
  
const alphabet_b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+.";
function sint_to_b64( val )
{
    // convert a val -127..127 to b64like encoded
    val = val + 127;
    return alphabet_b64[(val/64)>>0] + alphabet_b64[val%64]; // >> 0 for convert to int
}
function b64_to_sint( code )
{
    // revert operation than b64_to_sint
    idx0 = alphabet_b64.indexOf( code[0] );
    idx1 = alphabet_b64.indexOf( code[1] );
    let val = idx0 * 64 + idx1;
    val = val - 127;
    return val;
}
function b64_to_ushint( code )
{
    // b64 to 0..4095
    idx0 = alphabet_b64.indexOf( code[0] );
    idx1 = alphabet_b64.indexOf( code[1] );
    let val = idx0 * 64 + idx1;
    return val;
}
console.log( "sint_to_b64: -127: " + sint_to_b64( -127 ) );
console.log( "sint_to_b64: 5: " + sint_to_b64( 5 ) );
console.log( "sint_to_b64: 127: " + sint_to_b64( 127 ) );
console.log( "b64_to_sint: AA: " + b64_to_sint( "AA" ) );
console.log( "b64_to_sint: CE: " + b64_to_sint( "CE" ) );
console.log( "b64_to_sint: D+: " + b64_to_sint( "D+" ) );
console.log( "b64_to_ushint: ..: " + b64_to_sint( ".." ) );

  function updateMotorsAndSensors(){
    //console.log("DBG: updateMotorsAndSensors: start" );
    if( websocket == 0 )
    {
      console.log("DBG: updateMotorsAndSensors: no ws" );
    }
    else
    {
      //console.log("DBG: updateMotorsAndSensors: sending motor command" );
      var msg = 'motor_';
      for (var i = 0; i < nNbrMotorInterface; i++ )
      {
        msg += "P" + sint_to_b64(aOrderMotor[i]);
      }
      websocket.send( msg );
    }
    // setTimeout( updateMotorsAndSensors, 50 ); // it's better to prepare an update after receiving datas, so we're not accumulating calls. Else: Arduino: "ERROR: Too many messages queued", then crash
  }
  
   function gradient(a, b) { 
        return (b.y-a.y)/(b.x-a.x); 
    } 

   function gradient4(x1,y1,x2,y2) { 
        return (y2-y1)/(x2-x1); 
    }
    
    function bzCurveXY(ctx2d, points, f, t) { 
        // points are a list of (.x,.y)
        console.log("DBG: bzCurve: start" );
        if (typeof(f) == 'undefined') f = 0.3; 
        if (typeof(t) == 'undefined') t = 0.6; 
      
        ctx2d.beginPath(); 
        ctx2d.moveTo(points[0].x, points[0].y); 
      
        var m = 0; 
        var dx1 = 0; 
        var dy1 = 0; 
          
        var preP = points[0]; 
          
        for (var i = 1; i < points.length; i++) { 
            var curP = points[i]; 
            nexP = points[i + 1]; 
            if (nexP) { 
                m = gradient(preP, nexP); 
                dx2 = (nexP.x - curP.x) * -f; 
                dy2 = dx2 * m * t; 
            } else { 
                dx2 = 0; 
                dy2 = 0; 
            } 
              
            ctx2d.bezierCurveTo( 
                preP.x - dx1, preP.y - dy1, 
                curP.x + dx2, curP.y + dy2, 
                curP.x, curP.y 
            ); 
          
            dx1 = dx2; 
            dy1 = dy2; 
            preP = curP; 
        } 
        ctx2d.stroke(); 
    } 

function bzCurveY(ctx2d, times, points, f, t) { 
        // one list is time of point, points are values
        console.log("DBG: bzCurveY: start" );
        console.log( times );
        console.log( points );
        if (typeof(f) == 'undefined') f = 0.3; 
        if (typeof(t) == 'undefined') t = 0.6; 
      
        ctx2d.beginPath(); 
        ctx2d.moveTo(times[0], points[0]); 
      
        var m = 0; 
        var dx1 = 0; 
        var dy1 = 0; 
          
        var iPrep = 0; 
          
        for (var i = 1; i < points.length; i++) {        
            if (points[i + 1]) { 
                m = gradient4(times[iPrep],points[iPrep],times[i+1],points[i+1]); 
                dx2 = times[i+1]-times[i] * -f; 
                dy2 = dx2 * m * t; 
            } else { 
                dx2 = 0; 
                dy2 = 0; 
            } 
              //en train d'ecrire cette fonction pour n'avoir que 2 listes: une time et une avec des valeurs pour chaque capteurs et quand c'est fini on copie ce fichier dans le .ino
            ctx2d.bezierCurveTo( 
                times[iPrep] - dx1-times[0], points[iPrep] - dy1, 
                times[i] + dx2-times[0], points[i] + dy2, 
                times[i]-times[0], points[i]
            ); 
          
            dx1 = dx2; 
            dy1 = dy2; 
            iPrep = i; 
        } 
        ctx2d.stroke(); 
    }
  
  function drawGraph(ctx2d, times, points, f, t) { 
    w = ctx2d.canvas.clientWidth;
    h = ctx2d.canvas.clientHeight;
    //console.log(w);
    ctx2d.clearRect(0, 0, w, h);
    ctx2d.beginPath(); // reset lines
    //ctx2d.moveTo( 0, h/2 );
    // ctx2d.lineTo( w, h/2 );
    dx = times[times.length-1] - times[0];
    halfdy = 128+2;
    ctx2d.moveTo( 0, h/2+points[i]*h/2/halfdy );
    for (var i = 1; i < points.length; i++) 
    {    
        ctx2d.lineTo( (times[i]-times[0])*w/dx, h/2 - points[i]*h/2/halfdy ); // - because the canvas is oriented to the bottom
    }
    ctx2d.stroke();
  }
  
  function initPosDevices()
  {
    for (var j = 0; j < 16; j++ )
    {
        aaPosDevices.push([]);
        for (var i = 0; i < nNbrValByDevice; i++ )
        {
            //aaPosDevices[j].push({ x: i, y: i });
            aaPosDevices[j].push( i%256 );
        }
    }
    
    for (var i = 0; i < nNbrValByDevice; i++ )
    {
        aTimes.push(Date.now()/1000-(nNbrValByDevice-i)/10)
    }
    
    var cv = document.getElementById("Motor1_graph"); 
    aListCtx.push( cv.getContext("2d") );
    
    var cv2 = document.getElementById("Motor2_graph"); 
    aListCtx.push( cv2.getContext("2d") );
    
    var cv3 = document.getElementById("Motor3_graph"); 
    aListCtx.push( cv3.getContext("2d") );
    
    var cv4 = document.getElementById("Motor4_graph"); 
    aListCtx.push( cv4.getContext("2d") );
    
    var cv5 = document.getElementById("Motor5_graph"); 
    aListCtx.push( cv5.getContext("2d") );
    
    var cv6 = document.getElementById("Motor6_graph"); 
    aListCtx.push( cv6.getContext("2d") );
    
    for (var i = 0; i < nNbrMotorInterface; i++ )
    {
        aListCtx[i].setLineDash([0]); 
        aListCtx[i].lineWidth = 2; 
        aListCtx[i].strokeStyle = "green"; 
        aOrderMotor.push( 0 );
    }
  }
  function addTimeToVal()
  {
    var d = new Date(); // for now
    aTimes.shift()
    aTimes.push(Date.now()/1000);
  }
  
  function updateDeviceVal(idx, pos)
  {
    //console.log("DBG: updateDeviceVal: idx: " + idx + ", pos: " + pos );
    aaPosDevices[idx].shift()
    aaPosDevices[idx].push(pos);
    drawGraph( aListCtx[idx], aTimes, aaPosDevices[idx], 0.3, 1 ); 
  }
  function updateSensorVal( idx, val )
  {
    let color = pseudoColorFrom12Bit(val);
    if( idx == 0 )
    {
        document.getElementById('Sens1_val').innerHTML = val;
        document.getElementById('Sens1_box').style.background = color;
    }
    else if( idx == 1 )
    {
        document.getElementById('Sens2_val').innerHTML = val;
        document.getElementById('Sens2_box').style.background = color;
    }
    else if( idx == 2 )
    {
        document.getElementById('Sens3_val').innerHTML = val;
        document.getElementById('Sens3_box').style.background = color;
    }
    else if( idx == 3 )
    {
        document.getElementById('Sens4_val').innerHTML = val;
        document.getElementById('Sens4_box').style.background = color;
    }
  }
  
  function simulateValue()
  {
    addTimeToVal()
    updateDeviceVal( 0, 128*Math.sin( Date.now()/(2*1000) ) );
    updateDeviceVal( 1, 128*Math.sin( (Date.now()+3000)/(2*1000) ) );
    setTimeout( simulateValue, 50 );
  }
  
  function sliderChange( id, idx, val )
  {
    console.log("DBG: sliderChange: id: " + id, ", val: " + val );
    let val_order = ((val * 254 / 100) - 127 )>>0;
    console.log("DBG: sliderChange: val_order: " + val_order );
    aOrderMotor[idx] = val_order;
  }
  
function refreshPage()
{
    if( no_update_cpt < 5 )
    {
        no_update_cpt += 1;
        if( no_update_cpt == 5 )
        {
            document.getElementById('update_state').innerHTML = "lost";
        }
    }
    
    setTimeout( refreshPage, 1000 );
}

initPosDevices();
setTimeout( refreshPage, 1000 );
//setTimeout( simulateValue, 200 );
//setTimeout( updateMotorsAndSensors, 2000 );
if(0)
{
    let fakeevent = Object()
    fakeevent.data = "Pos_CcAnC3C8CiB.01..4567890123456789B";
    onMessage(fakeevent)
    setTimeout( ()=>{onMessage(fakeevent)}, 6000 );
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

#define NBR_MOTOR     6

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


void notifyClients() {
  ws.textAll(String(ledState));
}

int find_char( const char * buf, char ch )
{
  // find first char in buf, return position idx or -1 if not found
  // buf must end with \0
  const char * p =  buf;
  while( *p )
  {
    if( *p == ch )
    {
      return p-buf;
    }
    ++p;
  }
  Serial.print( "DBG: find_char: char not found in buf: " ); Serial.println( ch );
  return -1;
}

const char alphabet_b64[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+.";
void sint_to_b64( sbyte val, char * dst )
{
  // convert a val -127..127 to b64like encoded
  int val2 = int(val) + 127;
  dst[0] = alphabet_b64[val2/64];
  dst[1] = alphabet_b64[val2%64];
}

sbyte b64_to_sint( const char * code )
{
    // revert operation than b64_to_uint
    int idx0 = find_char( alphabet_b64, code[0] );
    int idx1 = find_char( alphabet_b64, code[1] );
    int val = (idx0 << 6) + idx1;
    val = val - 127;
    return sbyte(val);
}

void ushint_to_b64( unsigned short int val, char * dst )
{
  // convert a val 0..4095 to b64like encoded
  // overflow not handled!
  
  dst[0] = alphabet_b64[val/64];
  dst[1] = alphabet_b64[val%64];
}


void sensors_get( char * buf )
{
  // fill buf with the current sensor state
  buf[0] = (uint8_t)analogRead(PIN_AN_1)>>2;
  buf[1] = (uint8_t)analogRead(PIN_AN_2)>>2;
  buf[2] = (uint8_t)analogRead(PIN_AN_3)>>2;

  buf[3] = (uint8_t)digitalRead(PIN_DIGI_1)>>2;
  buf[4] = (uint8_t)digitalRead(PIN_DIGI_2)>>2;
  buf[5] = (uint8_t)digitalRead(PIN_DIGI_3)>>2;

  buf[10] = (uint8_t)analogRead(PIN_BAT)>>2;
}

void sensors_get_b64( char * buf )
{
  // fill buf with the current sensor state
  // analogRead return a value in (0-1023 for 10 bits or 0-4095 for 12 bits).
  int val;
  val = analogRead(PIN_AN_1);
  ushint_to_b64( val, &buf[0] );

  val = analogRead(PIN_AN_2);
  ushint_to_b64( val, &buf[2] );

  val = analogRead(PIN_AN_3);
  ushint_to_b64( val, &buf[4] );


  val = analogRead(PIN_DIGI_1);
  ushint_to_b64( val, &buf[6] );
  
  val = analogRead(PIN_DIGI_2);
  ushint_to_b64( val, &buf[8] );
  
  val = analogRead(PIN_DIGI_3);
  ushint_to_b64( val, &buf[10] );

  
  val = analogRead(PIN_DIGI_1);
  ushint_to_b64( val, &buf[12] );

  buf[19] = (uint8_t)analogRead(PIN_BAT)>>2;
}


void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    //Serial.print("DBG: handleWebSocketMessage: data: "); Serial.println( (char*)data );
    if (strcmp((char*)data, "toggle") == 0) 
    {
      ledState = !ledState;
      notifyClients();
    }
    if (strncmp((char*)data, "motor",5) == 0) 
    {
      if( 0 )
      {
        // fake decoding & encoding

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

      // real decoding and encoding
      if( 1 )
      {
        // datas are: motor_PXX with P: the command type: P: Position, V: Velocity, F: Fake; and XX: the b64 encoded position -127..127
        for(int i = 0; i < NBR_MOTOR; ++i )
        {
          const int nFirstCharPos = 6; // first char after Motor_
          char command = data[nFirstCharPos+i*3];
          sbyte val = b64_to_sint( (char*) & (data[nFirstCharPos+i*3+1]) );
          if( command == 'P' )
          {
            dym.sendPosition( i, val );
          }
          else if( command == 'V' )
          {
            dym.sendVelocity( i, val );
          }
          else if( command == 'F' )
          {
            // Fake order
            // Nothing
          }
          else
          {
            Serial.print( "DBG: handleWebSocketMessage: unknown command: " ); Serial.println( command );
          }
        }

        // prepare answer
        static char sendpos[] = "Pos_XXxxXXxxXXxx01234567890123456789B"; // TODO: Real answer for sensors (we duplicate size for them as they will be b64encoded also)
        const int nFirstCharPosRet = 4;
        const sbyte * allMotorPos = dym.getAllPositions();
        for(int i = 0; i < NBR_MOTOR; ++i )
        {
          sint_to_b64( allMotorPos[i], &sendpos[nFirstCharPosRet+i*2] );
        }
        sensors_get_b64( &sendpos[nFirstCharPosRet+6*2] );
        //Serial.print("DBG: handleWebSocketMessage: sendpos: "); Serial.println( sendpos );
        ws.textAll(sendpos);
      }
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
  Serial.print( "DBG: processor: var: " ); Serial.println( var );
  if(var == "STATE"){
    if (ledState){
      return "ON";
    }
    else{
      return "OFF";
    }
  }
  if(var == "BOARD_ID")
  {
    return getArduinoId();
  }
  return "ERR: processor: var not found!";
  //return String();
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

void replace_in_buf( char * dst, const char * old_cz, const char * new_cz )
{
  // replace in dst the string old by string dst.
  // don't change the size of dst!
  Serial.println("DBG: in replace buf");
  char * p = dst;
  int len_old = strlen(old_cz);
  int len_new = strlen(new_cz);
  Serial.println(len_old);
  Serial.println(len_new);
  while( *p )
  {
    if( strncmp(p,old_cz,len_old) == 0 )
    {
      Serial.println("found");
      memcpy(p,new_cz,len_new);
      p += len_old;
    }
    ++p;
    Serial.println(int(p));
  }
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

  int bConnectToBoxFirst = 1;
  int bConnected = 0;
  
  if( bConnectToBoxFirst )
  {
    // Connect to Wi-Fi
    /*
    Serial.println("Connecting to WiFi..");
    WiFi.begin(my_ssid, my_password);
    while (WiFi.status() != WL_CONNECTED) {
      Serial.print(".");
      delay(1000);
    }
    Serial.println("");
    // Print ESP Local IP Address
    Serial.println(WiFi.localIP());
    */
    bConnected = connectToWifi();
  }
  if(!bConnected)
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

  server.on("/motor", HTTP_GET, MotorHandler ); // Attention: ca c'est le handler html, le WebSocket est plus haut


  // Start server
  server.begin();
  Serial.println( "server started..." );

  lcd_print_message( "Serving on: ", getCurrentSSID() );
  lcd_print_message( getCurrentIP() );
  lcd_print_message( "Port: ", nNumPort );

  // change xxx by getArduinoId
  //replace_in_buf( (char *)index_html,"BOARD_ID_   ",getArduinoId() ); // we plan to change an read only memory ! :) => guru meditation (need to duplicate in ram or found another way)
  //replace_in_buf( (char *)index_html,"% ;","%%;" ); // we plan to change an read only memory ! :)

  if( 1 )
  {
    // internal test:
    char buf[] = "AA";
    sint_to_b64( -127, buf );
    Serial.print( "DBG: sint_to_b64: -127: " ); Serial.println( buf );

    sint_to_b64( 5, buf );
    Serial.print( "DBG: sint_to_b64: 5: " ); Serial.println( buf );

    sint_to_b64( 127, buf );
    Serial.print( "DBG: sint_to_b64: 127: " ); Serial.println( buf );

    Serial.print( "DBG: b64_to_sint: AA: " ); Serial.println( b64_to_sint("AA") );
    Serial.print( "DBG: b64_to_sint: CE: " ); Serial.println( b64_to_sint("CE") );
    Serial.print( "DBG: b64_to_sint: D+: " ); Serial.println( b64_to_sint("D+") );
  }
}

void loop() {
  ws.cleanupClients();
  digitalWrite(ledPin, ledState); // c'est bourrin, a chaque frame on réécris, meme si rien n'a changé!
  delay(10);
}

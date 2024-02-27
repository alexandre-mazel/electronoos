#include "ethernet_srv.h"
#include "definitions.h"
#include "config.h"

#include "world.h"

_frc frc;
_ethData ethData;

// TODO Alma: a quoi sert cette methode et que sont toutes ses variables utilisé partout ?!?
void _gpioMotorsPS()
{
/*
  dPS_Stop = (frc.f_mRelay && !frc.f_vRelay) || (frc.f_mPS_ON && !frc.f_vPS_ON);
  if (dPS_Stop && (f_status != STOPPED)) return;
  ethData.f_oRelay = (frc.f_mRelay) ? frc.f_vRelay : ethData.ps_relay;
  ethData.f_oPS_ON = (frc.f_mPS_ON) ? frc.f_vPS_ON : ethData.ps_on;

  if (ethData.f_oRelay && ethData.f_oPS_ON && !lastPS) {
    Serial.println("Delay TIME_BEFORE_POWERING_MOTORS");
    delay(TIME_BEFORE_POWERING_MOTORS);
  }
  if (ethData.f_oRelay) {
    digitalWrite(RELAY_PIN, HIGH);
    Serial.println("Relay ON");
  } else {
    digitalWrite(RELAY_PIN, LOW);
    Serial.println("Relay OFF");
  }
  if (ethData.f_oPS_ON) {
    digitalWrite(PS_ON_PIN, HIGH);
    Serial.println("PS ON");
  } else {
    digitalWrite(PS_ON_PIN, LOW);
    Serial.println("PS OFF");
  }
  if (ethData.f_oRelay && ethData.f_oPS_ON && !lastPS) {
    Serial.println("Delay TIME_BEFORE_MOVING_MOTORS");
    delay(TIME_BEFORE_MOVING_MOTORS);
  }
  lastPS = ethData.f_oRelay && ethData.f_oPS_ON;
  */
}

void gpioMotorsPS(bool on) 
{
  ethData.ps_relay = ethData.ps_on = on;
  _gpioMotorsPS();
}

EthernetSrv::EthernetSrv()
  : server_ ( cfg.eth_SrvDefaultPort )
  , cur_    ( 0 )
{

}

void EthernetSrv::init() 
{
  Ethernet.init(ETH_CS_PIN);

  byte ethMode = cfg.eth_Mode;
  world.ethernetAvailable_ = false;
  
  if (ethMode == ETH_DHCP) {
    // start the Ethernet connection:
    Serial.println("\nInitialize Ethernet with DHCP:");
    if (Ethernet.begin(cfg.eth_MAC, ETH_DHCP_TIMEOUT, ETH_DHCP_RESP_TIMEOUT) == 0) {
      Serial.println("Failed to configure Ethernet using DHCP");
      // Check for Ethernet hardware present
      if (Ethernet.hardwareStatus() == EthernetNoHardware) {
        Serial.println("Ethernet shield was not found.  Running without Ethernet support.");
        return;
      }
      if (Ethernet.linkStatus() == LinkOFF) {
        Serial.println("Ethernet cable is not connected.\n");
      }
      ethMode = ETH_STATIC_IP;
      // try to configure using IP address instead of DHCP:
      Serial.println("Trying to assign static IP:");
      Ethernet.begin(cfg.eth_MAC, cfg.eth_IP, cfg.eth_DNS, cfg.eth_Gateway, cfg.eth_Subnet);
    }
  }
  else {
    ethMode = ETH_STATIC_IP;
    Serial.println("Trying to assign static IP:");
    Ethernet.begin(cfg.eth_MAC, cfg.eth_IP, cfg.eth_DNS, cfg.eth_Gateway, cfg.eth_Subnet);
  }
  Serial.print((ethMode == ETH_DHCP) ? "DHCP assigned IP : " : "Static IP        : "); Serial.println(Ethernet.localIP());
  Serial.print("Subnet mask      : "); Serial.println(Ethernet.subnetMask());
  Serial.print("Gateway          : "); Serial.println(Ethernet.gatewayIP());
  Serial.print("DNS server       : "); Serial.println(Ethernet.dnsServerIP());
  Serial.print("Listening port   : "); Serial.println(cfg.eth_SrvDefaultPort);
  Serial.println();
  world.ethernetAvailable_ = true;
  server_.begin();
  ethData.session = random(256);
  Serial.print("Session #        : "); Serial.println(ethData.session);
}

void EthernetSrv::setSTDBY(bool new_value) {
  ethData.stdby_m = new_value;
  digitalWrite(STANDBY_LED_PIN, ethData.stdby_m);
}

void EthernetSrv::process() {
  EthernetClient client = server_.available();
  int p = 0;

  if (client) {
    if (client.connected())

    while (client.available() && (p < 30)) {
      char c = client.read();
      p++;
      if (c == '\n') {
        cur_ = 0;

        if (strncmp(chaine_, "POST /", 6) == 0) {
          Serial.println(chaine_);
          if (strncmp(chaine_+6, "?cmd=", 5) == 0) {
            if (strncmp(chaine_+11, "stdby", 5) == 0) {
              ethData.stdby_m = !ethData.stdby_m;
              digitalWrite(STANDBY_LED_PIN, ethData.stdby_m);
              Serial.print("ETH CMD Standby ");
              Serial.println(ethData.stdby_m ? "ON" : "OFF");
            } else if (strncmp(chaine_+11, "user", 4) == 0) {
              ethData.user_m = !ethData.user_m;
              Serial.print("ETH CMD User ");
              Serial.println(ethData.user_m ? "ON" : "OFF");
            } else if (strncmp(chaine_+11, "config_", 7) == 0) {
              byte new_mode = -1;
              switch (chaine_[18]) {
                case 'n' : new_mode = NORMAL; break;
                case 'd' : new_mode = CONFIG_DEBUG; break;
              }
              if (new_mode != -1) {
                Serial.println("ETH CMD Config");
                if ((ethData.mode == NORMAL) && (new_mode == CONFIG_DEBUG)) {
                    Serial.print("Switched from NORMAL to DEBUG mode ");
                } else {
                  if ((ethData.mode == CONFIG_DEBUG) && (new_mode == NORMAL)) {
                    Serial.println("Return to NORMAL mode");
                  }
                }
                ethData.mode = new_mode;
              }
            }
          } else if (strncmp(chaine_+6, "param?", 6) == 0) {
            char * idx = strstr(chaine_+13, "=");
            if (idx == NULL) return;
            chaine_[idx - chaine_] = '\0';
            uint8_t index = atoi(chaine_+13);
            bool value = (idx[1] == '1');
            if (chaine_[12] == 'f') {
              switch (index) {
                case 0: frc.f_mPerm = value; break;
                case 1: frc.f_mTemp = value; break;
                case 2: frc.f_mPir = value; break;
                case 3: frc.f_mRelay = value; _gpioMotorsPS(); break;
                case 4: frc.f_mPS_ON = value; _gpioMotorsPS(); break;
                case 5: frc.f_mSleep_m = value; break;
              }
            } else if (chaine_[12] == 'v') {
              switch (index) {
                case 0: frc.f_vPerm = !frc.f_vPerm; break;
                case 1: frc.f_vTemp = !frc.f_vTemp; break;
                case 2: frc.f_vPir = !frc.f_vPir; break;
                case 3: frc.f_vRelay = value; _gpioMotorsPS(); break;
                case 4: frc.f_vPS_ON = value; _gpioMotorsPS(); break;
                case 5: frc.f_vSleep_m = value; break;
              }
            }
          }
          client.stop();
        } else if (strncmp(chaine_, "GET /", 5) == 0) {
          if (strncmp(chaine_+5, "data", 4) == 0) {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-Type: text/plain");
            client.println();
            for (int k = 0; k < 4; k++){
              client.print(ethData.byte[k] >> 4, HEX);
              client.print(ethData.byte[k] & 0xF, HEX);
            }
          } else {
            Serial.println("Sending web page ... ");
            client.println(F("HTTP/1.1 200 OK"));
            client.println(F("Content-Type: text/html"));
            client.println(F("Connection: close"));  // the connection will be closed after completion of the response
            client.println();
            client.println(F("<!DOCTYPE HTML>"));
            client.println(F("<html lang=\"fr\">"));
            client.println(F("<head>"));
            client.println(F("<meta charset=\"UTF-8\">"));
            client.println(F("<meta name=\"author\" content=\"François MARIONNET - FEMTO-ST / AS2M / ENSMM - Besançon (France)\">"));
            client.println(F("<title>Snakable 2021</title>"));
            client.println(F("<link rel=\"icon\" href=\"data:,\">"));
            client.println(F("<style>html{margin:0;padding:0;background-color:rgb(0,16,92);}\n#ctn{position:absolute;left:0;right:0;top:0;bottom:0;margin:auto;width:640px;height:auto;max-width: 100%;min-width:600px;max-height:100%;background-color:rgb(79,129,189);}"));
            client.println(F("#ttl {font-family:Arial;font-size:28px;color:#23236f;text-shadow: 1px 1px 2px #ffc5cf;margin:12px;padding-top:5px;padding-bottom:5px;}\n#s0,#s1{margin-top:10px;border:3px solid rgb(56,93,138);border-radius:16px;background-color:rgb(112,146,190);width:460px;}"));
            client.println(F("table{display:grid;}\n#p0 td:not(:first-child){width:70px;}\n#p0 td:first-child:not([colspan]){width:100px;text-align:left;}\n#s0{padding-bottom:10px;}\n.sct{background-color:#735bcc;height:20px;margin-top:0px;padding-top:0px;border-top-left-radius:13px;border-top-right-radius:13px;font-family:arial;font-size:18px;"));
            client.println(F("margin-bottom:10px;border-bottom:3px solid rgb(56,93,138);color:#0f0d6f;}\n.g,.r,.o{border-color:#8a8484;background-color:#777676;height:19px;width:30px;padding-top:11px;}\n.o.a{background-color:orange;}\n.r.a{background-color:#d73131;border-color:rgb(106,7,22);color:white;}\n.g.a {background-color:#45e64b;border-color:rgb(151,168,153);}\n"));
            client.println(F("td[colspan='5']{text-align:center;}\n.switch {position:relative;display:inline-block;width:45px;height:24px;}\n.switch input{opacity:0;width:0;height:0;}\n.slider {position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background-color:#ccc;-webkit-transition:.4s;transition:.4s;}"));
            client.println(F(".slider:before {position:absolute;content:'';height:18px;width:18px;left:4px;bottom:3px;background-color:white;-webkit-transition:.4s;transition:.4s;}\ninput:checked:disabled + .slider{background-color:#ccc;}\ntr{height:26px;}"));
            client.println(F("input:checked:not(disabled) + .slider{background-color:#065595;}\ninput:focus + .slider{box-shadow: 0 0 1px #065595;}\ninput:checked + .slider:before{-webkit-transform:translateX(19px);-ms-transform:translateX(19px);transform:translateX(19px);}"));
            client.println(F("td[colspan='4']{background-color:rgb(98,126,181);}\n.c button,td[colspan='5'] button{margin-top:15px;width:140px;height:30px;background-color:lightgrey;margin-bottom:15px;}\n.slider.round {border-radius:34px;}\n.slider.round:before {border-radius:50%;}\n#ctn:not(.n,.d) #p0,#ctn:not(.p) #p1,#ctn:not(.m) #p2{display:none;}\n#ctn:not(.d) td:nth-child(n+3){display:none;}\n#ctn:not(.d) #p0 tr:nth-child(1){display:none;}\n#ctn.n .n,#ctn.p .p,#ctn.m .m,#ctn.d .d{display:none;}"));
            client.println(F("[ip]{width:28px;text-align:right;}\n[ms]{font-family:\"Courier new\",\"Arial\";width:15px;text-align:right;}</style>"));
            client.print(F("</head><body><center><div id='ctn' class='n'></div></center><script>\nlet val=Array(8).fill(false);\nlet frc = Array(8).fill(false);\nlet bch=Array(8).fill(false);\nlet k=0;"));
            client.println(F("let r=0;let s=[[['Inputs / Outputs',[['','Perm mains','g'],['','Temp mains','g'],['','PIR','g'],['','PS relay','g'],['','PS_ON','g']]],['Modes / Status',[['','Sleep mode','o'],['v','Standby mode','o'],['v','User mode','g'],['l','PIR counter','cnt'],['l','Mode','mod'],['l','Status','sta'],['b','StandBy','?cmd=stdby']]]]];"));
            client.println(F("let str=\"<div id='ttl'>SNAKABLE 2021 monitoring</div>\";\nfor (let p=0;p<s.length;p++){\n"));
            client.println(F("str+=\"<div id='p\"+p+\"'>\";\nfor(let i=0;i<s[p].length;i++){\nstr+=\"<div id='s\"+i+\"'><div class='sct'>\"+s[p][i][0]+'</div><table><tbody>'+((s[p][i][1][0][0]=='')?\'<tr><td></td><td>Program</td><td>Auto/Man</td><td>Off/On</td><td>Effective</td></tr>':'');"));
            client.println(F("for (j=0;j<s[p][i][1].length;j++){\nswitch (s[p][i][1][j][0]){\ncase 'u':str+='<tr><td>'+s[p][i][1][j][1]+\"</td><td colspan='4'><select id='b\"+(k++)+\"'>\";\nfor(let l=0;l<usb.length;l++) str+=\"<option value='\"+l+\"'>\"+usb[l]+\"</option>\";\nstr+=\"</select></td></tr>\";break;"));
//                client.println(F("case 'd':str+='<tr><td>'+s[p][i][1][j][1]+\"</td><td colspan='4'><select id='b\"+(k++)+\"'><option value='0'>DHCP</option><option value='1'>Static IP</option></select></td></tr>\";break;"));
//                client.println(F("case 'm':str+='<tr><td>'+s[p][i][1][j][1]+\"</td><td colspan='4'>\"+mask(6, false)+\"</tr>\";break;"));
//                client.println(F("case 'i':str+='<tr><td>'+s[p][i][1][j][1]+\"</td><td colspan='4'>\"+mask(4)+\"</tr>\";break;"));
//                client.println(F("case 'x':str+='<tr><td>'+s[p][i][1][j][1]+\"</td><td><input id='b\"+(k++)+\"' type='checkbox'></input></td></tr>\";break;"));
//                client.println(F("case 'e':str+='<tr'+((p==2 && i==1)?' id=\\\"'+(r++)+'\\\" or=\\\"'+s[p][i][1][j][2]+'\\\"':'')+'><td>'+s[p][i][1][j][1]+\"</td><td><input type='number' id='b\"+(k++)+\"'></input></td></tr>\";break;"));
            client.println(F("case 'b':str+=\"<tr><td colspan='5'><button id='b\"+(k++)+\"' onclick=\\\"postData('\"+s[p][i][1][j][2]+\"')\\\">\"+s[p][i][1][j][1]+\"</button></td></tr>\";break;"));
//                client.println(F("case 'c':str+=\"<tr><td colspan='5'><button id='b\"+(k++)+\"' onclick=\\\"tri(\"+s[p][i][1][j][2]+\")\\\">\"+s[p][i][1][j][1]+\"</button></td></tr>\";break;"));
            client.println(F("case 'l':str+='<tr><td>'+s[p][i][1][j][1]+\"</td><td colspan='4' id='\"+s[p][i][1][j][2]+\"'></td></tr>\";break;"));
            client.println(F("case 'v':str+='<tr><td>'+s[p][i][1][j][1]+\"</td><td><button id='b\"+(k++)+\"' class='\"+s[p][i][1][j][2]+\"' disabled='disabled'></button></td><td colspan='3'></td></tr>\";break;"));
            client.println(F("case '':str+='<tr><td>'+s[p][i][1][j][1]+\"</td><td><button id='b\"+k+\"' class='\"+s[p][i][1][j][2]+\"' disabled='disabled'></button></td><td><label class='switch'><input id='f\"+k+\"' type='checkbox'><span class='slider round'></span></label></td>\";"));
            client.println(F("str+=\"<td><label class='switch'><input id='v\"+k+\"' type='checkbox'><span class='slider round'></span></label></td><td><button id='r\"+(k++)+\"' class='\"+s[p][i][1][j][2]+\"' disabled='disabled'></button></td></tr>\";break;"));
            client.println(F("}\n}\nstr+='</tbody></table></div>';\n}\nstr+='</div>';\n}\nstr+=\"<div class='c'><button class='n' onclick=chgMode('n')>Back to normal mode</button><button class='d' onclick=chgMode('d')>Debug</button></div>\""));
            client.println(F("document.getElementById('ctn').innerHTML=str;\nfunction set(id,val_f,val_v){\ndocument.getElementById('f'+id).checked=frc[id]=val_f;\ndocument.getElementById('v'+id).checked=val[id]=val_v;\nupd(id);\n}"));
            client.println(F("function config(on){\ndocument.getElementById('ctn').classlist.toggle('a',on);\n}\nfunction upd(v){\nif ((v<3)||(v==5)) document.getElementById('r'+v).classList.toggle('a',frc[v]?val[v]:bch[v]);\n}\n"));
            client.println(F("const btn=document.getElementsByTagName('input');\nfor (let k=0;k<btn.length;k++){\nbtn[k].addEventListener('change',function(event){\nlet v=parseInt(this.id.substring(1));\nswitch (this.id[0]){\ncase 'f':frc[v]=this.checked;break;\ncase 'v':val[v]=this.checked;break;\n}\nupd(v);\npostData('param?'+this.id+'='+(this.checked?'1':'0'));\n});}"));
            client.print(F("let session="));
            client.print(ethData.session);
            client.println(F(";let lRes=[0,60,255,255];\nlet intervalID;"));
            client.println(F("var arrStatus=['Stopped','Moving','Stopping'];"));
            client.println(F("function toggle(m,n){"));
            client.println(F("document.getElementById(m+n).classList.toggle('a');bch[n]=!bch[n];upd(n);"));
            client.println(F("}"));
            client.println(F("function postData(cmd) {"));
            client.println(F("var xhr=new XMLHttpRequest();"));
            client.println(F("xhr.open('POST','/'+cmd,true);"));
            client.println(F("xhr.send();"));
            client.println(F("}"));
//                client.println(F("function hexToFlt(hexString){v=new DataView(new ArrayBuffer(4));v.setUint32(0,parseInt(hexString,16),true);return v.getFloat32(0);}"));
//                client.println(F("function setMode(v){document.getElementById('ctn').className=['n','d'][v];}"));
            client.println(F("function hexToDec(hexString){"));
            client.println(F("return parseInt(hexString,16);"));
            client.println(F("}\nfunction upd(v) {if ((v<3) || (v==5)) document.getElementById('r'+v).classList.toggle('a',frc[v]?val[v]:bch[v]);}\nfunction getData(){"));
            client.println(F("var xhr=new XMLHttpRequest();"));
            client.println(F("xhr.open('GET','/data',true);"));
            client.println(F("xhr.responseType='text/plain';"));
            client.println(F("xhr.onload=function(v){"));
            client.println(F("if (!xhr.response) return;"));
            client.println(F("let data=hexToDec(xhr.response.substring(0,2));let dif=data ^ lRes[0];"));
            client.println(F("if (dif & 0x01) toggle('b',0);"));
            client.println(F("if (dif & 0x02) toggle('b',1);"));
            client.println(F("if (dif & 0x04) toggle('b',2);"));
            client.println(F("if (dif & 0x08) toggle('b',3);"));
            client.println(F("if (dif & 0x10) toggle('b',4);"));
            client.println(F("if (dif & 0x20) toggle('b',5);"));
            client.println(F("if (dif & 0x40) toggle('b',6);"));
            client.println(F("if (dif & 0x80) toggle('b',7);"));
            client.println(F("lRes[0]=data; data=hexToDec(xhr.response.substring(2,4));dif=data ^ lRes[1];"));
            client.println(F("if (dif & 0x01) toggle('r',3);"));
            client.println(F("if (dif & 0x02) toggle('r',4);"));
            client.println(F("if (dif & 0x0C) {let f=(data>>2)&3;document.getElementById('ctn').className=['n','d'][f];document.getElementById('mod').innerHTML=(f)?'Debug':'Normal';}"));
            client.println(F("if (dif & 0x30) document.getElementById('sta').innerHTML = arrStatus[(data >> 4) & 3];"));
            client.println(F("lRes[1]=data;data=hexToDec(xhr.response.substring(4,6));"));
            client.println(F("if (data ^ lRes[2]) document.getElementById('cnt').innerHTML = data.toString();"));
            client.println(F("lRes[2]=data; data=hexToDec(xhr.response.substring(6,8));"));
            client.println(F("if ((data ^ lRes[3]) && (data!=session)) location.reload(true);"));
            client.println(F("lRes[3]=data;"));
            client.println(F("};"));
            client.println(F("xhr.send();"));
            client.println(F("}"));
            client.println(F("function chgMode(val){"));
            client.println(F("var xhr=new XMLHttpRequest();"));
            client.println(F("xhr.open('POST','/?cmd=config_'+val,true);"));
            client.println(F("xhr.responseType='text/plain';"));
            client.println(F("xhr.send();"));
            client.println(F("}"));
            client.println(F("getData();"));
            if (ethData.mode != NORMAL) {
              client.print(F("chgMode('"));
              client.print((ethData.mode == CONFIG_PARAMS) ? 'p' : (ethData.mode == CONFIG_DEBUG) ? 'd' : 'm');
              client.println(F("');"));
            }
            client.print(F("setInterval(getData, "));
            client.print(cfg.eth_UpdatePeriod * 50);
            client.println(F(");</script>"));
            client.println(F("</body>"));
            client.println(F("</html>"));
          }
          client.stop();
        }
      } else chaine_[cur_++] = c;
    }
  }
}
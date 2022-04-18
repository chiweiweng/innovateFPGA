#include <Wire.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>
#include <ESP8266mDNS.h>
#include <Adafruit_MotorShield.h>

MDNSResponder mdns;

// Replace with your network credentials
const char* ssid = "wes";  //asdfg
const char* password = "blablabla";  //12345678
int imax = 180;
int gear = 0; //0 for low, 1 for medium, 2 for high
int sped = 0; // speed
int smax = 4; // maximum speed
int dir  = 0; // direction
int Mspeed[5][3]={{  0,   0,   0},
                  { 45,  54,  63},
                  { 90, 109, 128},
                  {135, 163, 192},  
                  {180, 217, 255}};

ESP8266WebServer server(80);

int gpio0_pin = 0;
int gpio2_pin = 2;
int motorL = 0;
int motorR = 0;

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *Motor1 = AFMS.getMotor(1);
Adafruit_DCMotor *Motor2 = AFMS.getMotor(2);
Adafruit_DCMotor *Motor3 = AFMS.getMotor(3);
Adafruit_DCMotor *Motor4 = AFMS.getMotor(4);

//webpage
String getPage(){
String webPage = "";
webPage += "<html>";
webPage += "<meta http-equiv=Content-Type content=\"text/html; charset=big5\">";
webPage += "<title>Wifi RC Boat by Jau-Horng Chen</title>";
webPage += "<STYLE type=\"text/css\">";
webPage += "td.off {background: #ffffaf; color: #5f5f10; text-align: center; font-size: 6vmin}";
webPage += "td.on  {background: #bfbf20; color: #ffffff; text-align: center; font-size: 6vmin}";
webPage += "</STYLE>";
webPage += "<body>";
webPage += "<table border=0 cellspacing=1 cellpadding=3 align=center bgcolor=#dfdf20 width=100% height=100%>";

webPage += "<tr><td width = \"20%\" class=off onclick=\"parent.location='stop'\">Stop</td><td width = \"20%\" class=off>";
webPage += String(sped);
webPage += "/4</td><td width = \"20%\" class=";
webPage += (gear==0? "on" : "off");
webPage += " onclick=\"parent.location='low' \">Low </td><td width = \"20%\" class=";
webPage += (gear==1? "on" : "off");
webPage += " onclick=\"parent.location='med' \">Med </td><td width = \"20%\" class=";
webPage += (gear==2? "on" : "off");
webPage += " onclick=\"parent.location='high'\">High</td></tr>";

webPage += "<tr><td colspan=\"5\" class=off onclick=\"parent.location='inc'\">+</td></tr>";

webPage += "<tr><td width = \"20%\" class=";
webPage += (dir==-2? "on" : "off");
webPage += " onclick=\"parent.location='l2'\" >&lt&lt</td><td width = \"20%\" class=";
webPage += (dir==-1? "on" : "off");
webPage += " onclick=\"parent.location='l1'\" >&lt   </td><td width = \"20%\" class=";
webPage += (dir== 0? "on" : "off");
webPage += " onclick=\"parent.location='cc'\" >O     </td><td width = \"20%\" class=";
webPage += (dir== 1? "on" : "off");
webPage += " onclick=\"parent.location='r1'\" >&gt   </td><td width = \"20%\" class=";
webPage += (dir== 2? "on" : "off");
webPage += " onclick=\"parent.location='r2'\" >&gt&gt</td></tr>";

webPage += "<tr><td colspan=\"5\" class=off onclick=\"parent.location='dec'\">-</td></tr>";

webPage += "</table>";
webPage += "</div>";
webPage += "</body>";
webPage += "</html>";
return webPage;
}

void set_motor(){
  server.send(200, "text/html", getPage());
  motorL=Mspeed[abs(sped)][gear];
  motorR=Mspeed[abs(sped)][gear];
  if(dir==-2)
    motorR>>=2;
  else if(dir==-1)
    motorR>>=1;
  else if(dir==1)
    motorL>>=1;
  else if(dir==2)
    motorL>>=2;
  Motor1->setSpeed(motorR);  
  Motor2->setSpeed(motorL);
  Motor3->setSpeed(motorR);  
  Motor4->setSpeed(motorL);
  Serial.println(String(motorL)+","+String(motorR)+"\n");
  sped>0? Motor1->run(FORWARD) : Motor1->run(BACKWARD);
  sped>0? Motor2->run(FORWARD) : Motor2->run(BACKWARD);
  sped>0? Motor3->run(FORWARD) : Motor3->run(BACKWARD);
  sped>0? Motor4->run(FORWARD) : Motor4->run(BACKWARD);
}

void setup(void){
  // preparing GPIOs
  pinMode(gpio0_pin, OUTPUT);
  digitalWrite(gpio0_pin, HIGH);
  pinMode(gpio2_pin, OUTPUT);
  digitalWrite(gpio2_pin, HIGH);
  
  delay(1000);
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.println("");
  digitalWrite(gpio0_pin, LOW);
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  
  if (mdns.begin("esp8266", WiFi.localIP())) {
    Serial.println("MDNS responder started");
  }

 
  server.on("/", [](){
    server.send(200, "text/html", getPage());
  });
  server.on("/low", [](){
    //Serial.println("poked");
    gear = 0;
    set_motor();
  });
  server.on("/med", [](){
    gear = 1;
    sped = 3;
    set_motor();
  });
  server.on("/high", [](){
    gear = 2;
    sped = 4;
    set_motor();
  });  
  server.on("/stop", [](){
    sped = 0;
    dir  = 0;
    set_motor();
  });
  server.on("/l2", [](){
    dir = -2;
    set_motor();
  });
  server.on("/l1", [](){
    dir = -1;
    set_motor();
  });
  server.on("/cc", [](){
    dir = 0;
    set_motor();
  });
  server.on("/r1", [](){
    dir = 1;
    set_motor();
  });
  server.on("/r2", [](){
    dir = 2;
    set_motor();
  });
  server.on("/inc", [](){
    if(sped < smax)
      sped++;
    set_motor();
  });
  server.on("/dec", [](){
    if(sped > -smax)
      sped--;
    set_motor();
  });
  
  server.begin();
  Serial.println("HTTP server started");
  
  AFMS.begin(1600);  // create with the default frequency 1.6KHz
  
  // Set the speed to start, from 0 (off) to 255 (max speed)
  Motor1->setSpeed(0);
  Motor1->run(FORWARD);
  Motor2->setSpeed(0);
  Motor2->run(FORWARD);
  Motor3->setSpeed(0);
  Motor3->run(FORWARD);
  Motor4->setSpeed(0);
  Motor4->run(FORWARD);

  // turn on motor
  Motor1->run(RELEASE);
  Motor2->run(RELEASE);
  Motor3->run(RELEASE);
  Motor4->run(RELEASE);
}
 
void loop(void){
  server.handleClient();
  //gear = 1;
  //sped = 3;
  //set_motor;
} 

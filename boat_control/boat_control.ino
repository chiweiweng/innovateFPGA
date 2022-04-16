#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiClient.h>


const char* ssid = "asdfg";
const char* password = "12345678";
// const char* host = "192.168.1.23";
const char* host = "0.0.0.0";
const int port = 9999;


void setup(){
  int count = 0;
  
  Serial.begin(115200);
  delay(10);

  IPAddress ip_static(192, 168, 1, 20);    
  IPAddress ip_gateway(0,0,0,0); 
  IPAddress ip_subnet(255,255,255,0); 
  IPAddress ip_dns(0,0,0,0);
  //WiFi.config(ip_static, ip_gateway, ip_subnet, ip_dns); 
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
//  WiFi.config(ip_static, ip_gateway, ip_subnet, ip_dns);

  Serial.println("Connecting");

  while(WiFi.status() != WL_CONNECTED){
    delay(1000);
    Serial.print(".");
    count++;
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("Time for connection(s): ");
  Serial.print(count);
  Serial.println();
  Serial.println("IP address: ");
  Serial.print(WiFi.localIP());
  Serial.println();
}

void loop(){
    WiFiClient client;

    if (!client.connect(host, port)) {

        Serial.println("Connection to host failed");

        delay(1000);
        return;
    }

    Serial.println("Connected to server successful!");

    client.print("Hello from ESP32!");

    Serial.println("Disconnecting...");
    client.stop();

    delay(10000);
 
}


#include <ESP8266WiFi.h>
#include "DHT.h"

#define DHTPIN 0 // chan D3
#define DHTTYPE DHT11 // DHT 11
DHT dht(DHTPIN, DHTTYPE);


const char* ssid = "wifi";
const char* password = "pass";
const uint16_t port = 8080;
const char * host = "dia chi ip";

WiFiClient client_esp;
void esp_connect()
{
  do{
      client_esp.connect(host, port);
      Serial.println("Connecting to server ......");
      delay(1000);  
    }while ( !client_esp.connected());
    client_esp.print("ESP"); // thong bao cho server biet day la client do nhiet do do am
  Serial.println("Connected to server successful!");  
}
int esp_check_connect()
{
  return client_esp.connected();
}


void setup()
{ 
  Serial.begin(115200);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());
  
  dht.begin(); 
  esp_connect(); 
  delay(2000);
  dht.readHumidity();
  dht.readTemperature();
  delay(1000);
}
 
void loop()
{
    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (!esp_check_connect())
    {
      esp_connect();
      delay(2000);
      return;    
    }
    else
    {
      client_esp.print("esp8266");  //
      if (isnan(h) || isnan(t))
      {
        client_esp.print(-999);  // gui thong bao loi doc nhiet do do am
      }
      else
      {
        client_esp.print(t);
        client_esp.print("%"); // phan cach nhiet do do am
        client_esp.print(h);
      }    
    }
    delay(5000);
}

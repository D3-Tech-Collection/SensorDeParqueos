
#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "Undefined";
const char* password = "12345678.";
const char* mqtt_server = "3.77.251.252";
const int mqtt_port=1883;
const char* publishTopic="Undefined/parqueo/p";
const char* clientId="ESP32ClientUndefined354645667563467";

WiFiClient espClient;
PubSubClient client(espClient);
    
RF24 radio(4, 5);
const byte identificacion[6] = "00001";
int Array[2];

void setup(){
  Serial.begin(115200);
  radio.begin();
  Serial.println("Receiver Started....");
  radio.openReadingPipe(0, identificacion);   
  radio.setPALevel(RF24_PA_MIN);
  radio.startListening();              
  Serial.println("Waiting for data");
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();
}
void reconnect() {

  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect(clientId)) {
      Serial.println("connected");

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");

      delay(5000);
    }
  }
}
 
void loop()
{
  char txt[10];
  if ( radio.available() ){
    radio.read(&txt, sizeof(txt));
      String msg(txt);
      Serial.println(msg);
      int colonIndex = msg.indexOf(':');
  
  if (colonIndex != -1) {
    int x = msg.substring(1, colonIndex).toInt();
    int y = msg.charAt(colonIndex + 1) - '0';
    
    
    if (y == 0 || y == 1) {
      
      Serial.print("x: ");
      Serial.println(x);
      Serial.print("y: ");
      Serial.println(y);

      String topicToSend = String(publishTopic) + String(x);
      const char* finalTopicToSend = topicToSend.c_str();

      String yString = String(y);
      const char* stateToSend = yString.c_str();

      Serial.println(finalTopicToSend);

      client.publish(finalTopicToSend, stateToSend);

    } else {
      Serial.println("Invalid 'y' value");
    }
  } else {
    Serial.println("Invalid input format");
  }
    }
    if (!client.connected()) {
    reconnect();
  }
  client.loop();

}
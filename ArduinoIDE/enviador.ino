#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(7, 8); // CE, CSN

const byte address[6] = "00001";

const int parking1Pin = 2;
const int parking2Pin = 3;

const int parking1Number = 30;
const int parking2Number = 50;

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.openWritingPipe(address);
  radio.setPALevel(RF24_PA_MIN);
  radio.stopListening();
  pinMode(parking1Pin, INPUT_PULLUP);
  pinMode(parking2Pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(parking1Pin), interrupt1Pin, CHANGE);
  attachInterrupt(digitalPinToInterrupt(parking2Pin), interrupt2Pin, CHANGE);
}

void loop() {}

void interrupt1Pin() {
  int state = !digitalRead(parking1Pin);
  enviarDatosAlESP32(parking1Number, state);
}

void interrupt2Pin() {
  int state = !digitalRead(parking2Pin);
  enviarDatosAlESP32(parking2Number, state);
}

void enviarDatosAlESP32(int numeroParkeo, int estadoParqueo) {
  char mensaje[20];
  snprintf(mensaje, sizeof(mensaje), "P%d:%d", numeroParkeo, estadoParqueo); // Formato P1:0 o P2:1
  radio.write(mensaje, sizeof(mensaje));
  Serial.print("Enviado: ");
  Serial.println(mensaje);
}

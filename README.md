# 🚗 Parking Bot - Telegram MQTT Notifier 🤖

El Parking Bot es un bot de Telegram que te mantendrá informado sobre el estado de los parqueos en tiempo real utilizando MQTT. Puedes recibir notificaciones cuando un parqueo cambie de estado y consultar la disponibilidad de parqueos libres.

## 📝 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#%EF%B8%8F-instalación)
  - [Configuración del Entorno](#configuración-del-entorno)
  - [Armado del Circuito](#-armado-del-circuito)
  - [Código en el Arduino IDE](#-código-en-el-arduino-ide)
  - [Configuracion del backend en Visual Studio Code](#-configuracion-del-backend-en-visual-studio-code)
- [Uso](#-uso)
- [Comandos](#-comandos)
- [Demostracion](#-demostracion)
- [Autores](#-autores)


## 🚀 Características

- Recibe notificaciones en tiempo real cuando un parqueo cambia de estado (ocupado o libre).
- Consulta la disponibilidad de parqueos libres con un comando.
- Registro de comandos y mensajes en un archivo CSV para seguimiento.
- Interfaz de usuario intuitiva en Telegram para comenzar y obtener ayuda.
- Utiliza MQTT para la comunicación entre el servidor de parqueos y el bot.

## 📋 Requisitos

Antes de comenzar, asegúrate de tener lo siguiente:

- Una cuenta de Telegram 📱.
- Token de un bot de Telegram 🤖.
- Un servidor MQTT funcionando. Puedes utilizar el que viene en el repositorio especificamente en el .env y utlizar [hiveMQ](https://www.hivemq.com/demos/websocket-client/) 
- Python 3.8 o superior. sinolo tienes puedes descargarlo [aquí](https://www.python.org/downloads/) 
- Un módulo ESP32 🛠️.
- Para probar el funcionamiento necesitaras 2 NRF24L01
- Un arduino para poder hacer la simulacion de los parqueos

## 🛠️ Instalación

### Configuración del Entorno

1. Descarga e instala el [IDE de Arduino](https://www.arduino.cc/en/software) si aún no lo tienes instalado.

2. Opcionalmente, puedes utilizar un IDE de programación de texto, como [Visual Studio Code](https://code.visualstudio.com/download), para editar el código de manera más eficiente.

3. Abre el IDE de Arduino y configura las preferencias para agregar el soporte del ESP32. Ve a "Archivo" > "Preferencias" y en "URLs Adicionales de Gestor de Tarjetas", agrega el siguiente enlace:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```

4. Ve a "Herramientas" > "Placa" > "Gestor de Tarjetas" y busca "ESP32". Instala el soporte para el ESP32.

5. Desde el menú "Sketch", selecciona "Incluir Biblioteca" > "Administrar Bibliotecas" e instala las siguientes bibliotecas:
   - ArduinoJson (de Benoit Blanchon)
   - AsyncTCP (de dvarrel)
   - ESPAsyncTCP (de dvarell)
   - ESPAsyncWebSrv (de dvarrel)

6. Si deseas ejecutar el bot de Telegram en Python, asegúrate de tener Python instalado. Luego, instala las dependencias del proyecto ejecutando el siguiente comando en la terminal, en la carpeta del proyecto:
   ```bash
   pip install -r requirements.txt
   ```

## 🧩 Armado del Circuito
El circuito para pruebas consta de la siguiente manera:
- El enviador sera asi 
![enviador](/media/armado/enviador.png)
- El receptorsera asi
![receptor](/media/armado/receptor.png)

## 💻 Código en el Arduino IDE
1. Descarga el repositorio del proyecto:
   ```bash
   git clone https://github.com/ElJoamy/SensorDeParqueos.git
   ```
2. Abre el archivo [enviador.ino](/ArduinoIDE/enviador.ino) en el IDE de Arduino.
3. Ahora carga el codigo en el arduino
4. Abre el archivo [receptor.ino](/ArduinoIDE/receptor.ino) en el IDE de Arduino y modifico las siguientes lineas
   ```c
   const char* ssid = "RED DE WIFI A LA QUE TE CONECTARAS";
   const char* password = "CONTRASENA  LA QUETE CONECTARAS";
   const char* mqtt_server = "3.77.251.252"; //IP DEL SERVIDOR MQTT
   const int mqtt_port=1883; //PUERTO DEL SERVIDOR MQTT
   const char* publishTopic="Oficinas/parqueo/p"; //TOPIC AL QUE PUBLICARAS LOS MENSAJES ejemplo Oficinas/parqueo/p
   const char* clientId="ESP32ClientUndefined354645667563467"; //ID DEL CLIENTE MQTT puedes poner el que quieras
   ```
5. Ahora carga el codigo en el Esp32

## 🐍 Configuracion del backend en Visual Studio Code
1. Descarga el repositorio del proyecto:
   ```bash
   git clone https://github.com/ElJoamy/SensorDeParqueos.git
   ```
2. Modifca el archivo [.env.example](.env.example) en el directorio raíz de la aplicación y configura las siguientes variables de entorno:
   ```env
   TELEGRAM_BOT_TOKEN=TOKEN DETU BOT DE TELEGRAM
   CSV_FILENAME=usuarios_start 
   CSV_MENSAJES_FILENAME=mensajes_mqtt
   LOGS_CSV_FILENAME=logs
   MQTT_SERVER=3.77.251.252
   MQTT_PORT=1883
   SUBSCRIBE_TOPIC=DEBES PONER EL TOPIC AL QUE TE SUSCRIBIRAS POR EJEMPLO Oficinasa/parqueo/#
   ```
   Donde: 
   - `TELEGRAM_BOT_TOKEN` es el token de tu bot de Telegram.
   - `CSV_FILENAME` es el nombre del archivo CSV donde se guardarán los usuarios que inicien el bot.
   - `CSV_MENSAJES_FILENAME` es el nombre del archivo CSV donde se guardarán los mensajes que se envien por MQTT.
   - `LOGS_CSV_FILENAME` es el nombre del archivo CSV donde se guardarán los logs de los usuarios.
   - `MQTT_SERVER` es la dirección IP del servidor MQTT.
   - `MQTT_PORT` es el puerto del servidor MQTT.
   - `SUBSCRIBE_TOPIC` es el topic al que te suscribirás para recibir los mensajes.
3. Renombra el archivo `.env.example` a `.env`.
4. Ejecuta el codigo [main.py](main.py) para iniciar el bot con el siguiente comando:
   ```bash
   python main.py
   ```
5. Opcional: en el repositorio existe el archivo [prueba.py](prueba.py) que te permite enviar mensajes por MQTT para probar el funcionamiento del bot. Pero debes editar una cosa en el archivo y es la siguiente linea:
   ```python
   topics = ["Undefined/parqueo/p" + str(i) for i in range(1, 51)] #TOPIC AL QUE PUBLICARAS LOS MENSAJES ejemplo Oficinas/parqueo/p
   ```
   Donde:
   - `Oficinas/parqueo/p` es el topic al que se publicará el mensaje.
6. Ejecuta el codigo [prueba.py](prueba.py) para enviar mensajes por MQTT con el siguiente comando:
   ```bash
   python prueba.py
   ```
7. Ahora puedes probar el funcionamiento del bot en Telegram.
**OJO SOLO SE ENVIARA MENSAJES A TOSDOS LOS USUARIOS QUE HAYAN PUESTO /START EN EL BOT**

## 📱 Uso
- Inicia una conversación con el bot y usa el comando `/start` para comenzar.
- Usa el comando `/libres` para obtener una lista de parqueos disponibles.
- Recibirás notificaciones cuando los parqueos cambien de estado.
- Utiliza `/help` para obtener más información sobre cómo usar el bot.

## 🤖 Comandos

- `/start`: Inicia la conversación con el bot.
- `/libres`: Consulta la disponibilidad de parqueos libres.
- `/help`: Obtiene información sobre cómo utilizar el bot.

## 💡 Demostracion 
- ![](/imgs/demostracion.gif)

## 👥 Autores
- 👥 @ElJoamy
- 👥 @MarcosHT4
- 👥 @Dylan-Chambi
- 👥 @TDVCool123


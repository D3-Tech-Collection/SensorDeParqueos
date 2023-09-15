import paho.mqtt.client as mqtt
import random
import time
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Leer las variables de entorno
mqtt_server = os.getenv("MQTT_SERVER")
mqtt_port = int(os.getenv("MQTT_PORT"))

# Lista de topics
topics = ["Undefined/parqueo/p" + str(i) for i in range(1, 51)]

# Crear un cliente MQTT
client = mqtt.Client()

# Conectar al servidor MQTT
client.connect(mqtt_server, mqtt_port)

try:
    for topic in topics:
        # Generar un valor aleatorio entre 0 y 1
        valor = random.randint(0, 1)

        # Publicar el mensaje en el topic
        client.publish(topic, str(valor))

        print(f"Mensaje publicado en {topic}: {valor}")

    print("Todas las publicaciones han sido realizadas.")
    client.disconnect()

except KeyboardInterrupt:
    print("Publicación de mensajes detenida.")
    client.disconnect()

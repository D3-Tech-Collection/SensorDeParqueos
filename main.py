import telebot
import datetime
import paho.mqtt.client as mqtt
import csv
import os
import hashlib
from dotenv import load_dotenv
from parking import *

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Leer las variables de entorno
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
csv_filename = os.path.join("registros", os.getenv("CSV_FILENAME") + ".csv")
csv_mensajes_filename = os.path.join("registros", os.getenv("CSV_MENSAJES_FILENAME") + ".csv")
logs_csv_filename = os.path.join("registros", os.getenv("LOGS_CSV_FILENAME") + ".csv")
mqtt_server = os.getenv("MQTT_SERVER")
mqtt_port = int(os.getenv("MQTT_PORT"))
subscribe_topic = os.getenv("SUBSCRIBE_TOPIC")

# mqtt_server = "3.77.251.252"
# mqtt_port = 1883
# subscribe_topic = "Undefined/parqueo/#" 

bot = telebot.TeleBot(bot_token)
# Lista para almacenar chat_ids de usuarios que han enviado /start
usuarios_start = []

def cargar_usuarios_start():
    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.reader(file)
            usuarios_start.extend([int(row[0]) for row in reader])
    except FileNotFoundError:
        print(f"El archivo {csv_filename} no fue encontrado.")

def cargar_csv_mensajes():
    # Verificar si el archivo CSV existe
    if not os.path.exists(csv_mensajes_filename):
        # Si no existe, crear el archivo y agregar encabezados
        with open(csv_mensajes_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Numero de Parqueo", "Estado del Parqueo", "Hora y Fecha"])

    # Leer el archivo CSV
    mensajes = []
    try:
        with open(csv_mensajes_filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Omitir la primera fila (encabezados)
            mensajes = sorted(reader, key=lambda x: int(x[0].replace("p", "")))  # Ordenar por número de parqueo
    except FileNotFoundError:
        pass
    
    return mensajes

def actualizar_estado_parqueo(parqueo, estado, hora_fecha):
    # Cargar los mensajes existentes desde el archivo CSV
    mensajes = cargar_csv_mensajes()

    # Buscar si ya existe una fila para el parqueo específico
    for mensaje in mensajes:
        if mensaje[0] == parqueo:
            mensaje[1] = estado  # Actualizar el estado del parqueo
            mensaje[2] = hora_fecha  # Actualizar la hora y fecha
            break
    else:
        # Si no se encuentra, agregar una nueva fila
        mensajes.append([parqueo, estado, hora_fecha])

    # Sobrescribir el archivo CSV con los mensajes actualizados
    with open(csv_mensajes_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Numero de Parqueo", "Estado del Parqueo", "Hora y Fecha"])
        writer.writerows(mensajes)
    file.close()
    update_parking_states_from_csv(csv_mensajes_filename, parking_space_states)
    draw_parking_lot(rows, parking_spaces_per_row, parking_space_width, parking_space_length, space_between_rows, parking_space_states)

def guardar_usuarios_start():
    if not os.path.exists(csv_filename):
        # Si el archivo no existe, créalo
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for chat_id in usuarios_start:
                writer.writerow([chat_id])
    else:
        # Si el archivo ya existe, agrégale datos
        with open(csv_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            for chat_id in usuarios_start:
                writer.writerow([chat_id])

def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    topic = message.topic  # Obtener el topic del mensaje MQTT
    try:
        # Intentar procesar el mensaje MQTT como un mensaje de Telegram
        registrar_mensaje_mqtt(payload, topic)  # Llamar a la función para registrar el mensaje
        enviar_mensaje_a_usuarios(payload, topic)
    except AttributeError as e:
        # Si no es un mensaje de Telegram, simplemente registra el mensaje MQTT
        registrar_mensaje_mqtt(payload, topic)

client = mqtt.Client()
client.on_message = on_message
client.connect(mqtt_server, mqtt_port)
client.subscribe(subscribe_topic)
client.loop_start()

def enviar_mensaje_a_usuarios(mensaje, topic):
    try:
        if mensaje == "1":
            estado_parqueo = "ocupado"
        elif mensaje == "0":
            estado_parqueo = "libre"
        else:
            estado_parqueo = "desconocido"

        # Extraer el número de parqueo del topic
        numero_parqueo = topic.split("/")[-1]

        mensaje_log = f"El parqueo {numero_parqueo} esta {estado_parqueo}"

        # Mostrar el mensaje en la consola junto con la hora y fecha
        hora_fecha = obtener_hora_y_fecha()
        mensaje_log_con_hora = f"{mensaje_log}, Hora y Fecha: {hora_fecha}"
        print(mensaje_log_con_hora)

        # Enviar solo el mensaje MQTT a todos los usuarios que han enviado /start
        for chat_id in usuarios_start:
            bot.send_message(chat_id, mensaje_log)
            # enviar laimagen del parqueo
            bot.send_photo(chat_id, open('slotParking/parking_result.png', 'rb'))

    except Exception as e:
        print("Error al enviar el mensaje a Telegram:", str(e))

def registrar_mensaje_mqtt(mensaje, topic):
    try:
        hora_fecha = obtener_hora_y_fecha()
        # Extraer el número de parqueo del topic
        numero_parqueo = topic.split("/")[-1]
        
        # Actualizar el estado del parqueo en el archivo CSV
        actualizar_estado_parqueo(numero_parqueo, mensaje, hora_fecha)
        
        mensaje_log = f"Mensaje MQTT recibido para el parqueo {numero_parqueo} registrado en el archivo CSV"
        print(mensaje_log)
    except Exception as e:
        print("Error al registrar el mensaje MQTT:", str(e))

def guardar_registro(username, user_id, comando_o_mensaje):
    hora_fecha = obtener_hora_y_fecha()
    user_id_hash = hashlib.sha256(str(user_id).encode()).hexdigest()  # Encriptar el user_id
    with open(logs_csv_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, user_id, user_id_hash, comando_o_mensaje, hora_fecha])
        print(f"Registro guardado en logs.csv: {username}, {user_id}, {user_id_hash}, {comando_o_mensaje}, {hora_fecha}")

# Manejador de comandos /start
@bot.message_handler(commands=['start'])
def enviar_mensaje_start(message):
    try:
        chat_id = message.chat.id
        username = message.from_user.username
        comando_o_mensaje = "/start"
        
        guardar_registro(username, chat_id, comando_o_mensaje)
        
        hora_fecha = obtener_hora_y_fecha()
        user_id_hash = hashlib.sha256(str(chat_id).encode()).hexdigest()  # Encriptar el user_id
        mensaje_log = f"Comando /start recibido por {username}, ID: {user_id_hash}, Hora y Fecha: {hora_fecha}"
        print(mensaje_log)
        bot.reply_to(message, "¡Hola! Soy tu bot para controlar tu parqueo, te iré informando de los cambios que se realicen en los parqueos, puedes utilizar el comando /libres para poder saber que parqueos están libres y el comando /help para obtener ayuda.")
        
        # Agregar el chat_id del usuario a la lista de usuarios que han enviado /start
        if chat_id not in usuarios_start:
            usuarios_start.append(chat_id)
            guardar_usuarios_start()
    except Exception as e:
        print("Error al enviar el mensaje a Telegram:", str(e))

# Manejador de comandos /help
@bot.message_handler(commands=['help'])
def enviar_mensaje_help(message):
    try:
        chat_id = message.chat.id
        username = message.from_user.username
        comando_o_mensaje = "/help"
        
        guardar_registro(username, chat_id, comando_o_mensaje)
        
        hora_fecha = obtener_hora_y_fecha()
        user_id_hash = hashlib.sha256(str(chat_id).encode()).hexdigest()  # Encriptar el user_id
        mensaje_log = f"Comando /help recibido por {username}, ID: {user_id_hash}, Hora y Fecha: {hora_fecha}"
        print(mensaje_log)
        bot.reply_to(message, "Puedes utilizar el comando /libres para poder saber que parqueos están libres donde te dira un mensaje de los parqueos libres y te enviara una imagen de todos los parqueos libresademas puedes usar el comando /help para obtener ayuda. Recuerda que puedes usar el comando /start para iniciar el bot y poder recibir los mensajes de los parqueos libres  en tiempo real.") 
    except Exception as e:
        print("Error al enviar el mensaje a Telegram:", str(e))

# Manejador de comandos /libres
@bot.message_handler(commands=['libres'])
def enviar_parqueos_libres(message):
    try:
        chat_id = message.chat.id
        username = message.from_user.username
        comando_o_mensaje = "/libres"
        
        guardar_registro(username, chat_id, comando_o_mensaje)
        
        # Leer el archivo CSV de mensajes
        mensajes = cargar_csv_mensajes()

        # Filtrar los parqueos libres (estado 0)
        parqueos_libres = [mensaje for mensaje in mensajes if mensaje[1] == "0"]

        if parqueos_libres:
            # Construir un mensaje con los parqueos libres
            mensaje_libres = "Estos son los parqueos libres:\n\n"
            for parqueo in parqueos_libres:
                numero_parqueo, estado, hora_fecha = parqueo
                mensaje_libres += f"Parqueo {numero_parqueo}: Libre\n"

            # Enviar el mensaje de los parqueos libres al usuario que ejecutó el comando
            bot.send_message(chat_id, mensaje_libres)
            # Enviar la imagen del parqueo
            bot.send_photo(chat_id, open('slotParking/parking_result.png', 'rb'))

            # Registra en el log quién ha usado el comando /libres
            hora_fecha = obtener_hora_y_fecha()
            user_id_hash = hashlib.sha256(str(chat_id).encode()).hexdigest()  # Encriptar el user_id
            mensaje_log = f"Comando /libres utilizado por {username}, ID: {user_id_hash}, Hora y Fecha: {hora_fecha}"
            print(mensaje_log)
        else:
            bot.send_message(chat_id, "No hay parqueos libres en este momento.")
    except Exception as e:
        print("Error al enviar el mensaje de parqueos libres:", str(e))


def obtener_hora_y_fecha():
    ahora = datetime.datetime.now()
    return ahora.strftime("%H:%M:%S %d-%m-%Y")

def setup():
    cargar_usuarios_start()
    cargar_csv_mensajes()  # Cargar el archivo CSV
    print("El bot se ha iniciado a las:", obtener_hora_y_fecha())

if __name__ == "__main__":
    setup()
    bot.polling()
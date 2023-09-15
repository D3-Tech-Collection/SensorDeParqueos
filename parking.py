import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Ruta al archivo CSV
csv_mensajes_filename = os.path.join("registros", os.getenv("CSV_MENSAJES_FILENAME") + ".csv")

def draw_parking_lot(rows, parking_spaces_per_row, parking_space_width, parking_space_length, space_between_rows, parking_space_states):
    vertical_padding = 50
    car_width = 80
    car_height = 150

    background_color = "gray"
    line_color = "white"

    total_width = (parking_spaces_per_row + 2) * parking_space_width
    total_height = (rows * parking_space_length)

    if rows > 1:
        total_height += ((rows - 1) // 2) * space_between_rows

    total_height += 2 * vertical_padding

    image = Image.new("RGBA", (total_width, total_height), background_color)
    drawing = ImageDraw.Draw(image)

    font_size = 36
    font = ImageFont.truetype("arial.ttf", font_size)

    for row in range(rows):
        for parking_space in range(parking_spaces_per_row):
            x1 = (parking_space + 1) * parking_space_width
            y1 = row * parking_space_length

            if row > 0:
                y1 += (row // 2) * space_between_rows

            y1 += vertical_padding

            x2 = x1 + parking_space_width
            y2 = y1 + parking_space_length

            drawing.rectangle([(x1, y1), (x2, y2)], outline=line_color, width=2)

            if row % 2 == 0:
                drawing.line([(x1, y1), (x2, y1)], fill=background_color, width=2)
            else:
                drawing.line([(x1, y2 - 1), (x2, y2 - 1)], fill=background_color, width=2)

            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            text_x = center_x
            text_y = center_y + (-(abs(y1 - y2) // 2 - font_size // 2) if row % 2 == 0 else abs(y1 - y2) // 2 - font_size // 2)

            number = row * parking_spaces_per_row + parking_space + 1
            number_text = str(number)
            
            number_bbox = drawing.textbbox((text_x, text_y), number_text, font=font)
            
            text_x = text_x - (number_bbox[2] - number_bbox[0]) / 2
            text_y = text_y - (number_bbox[3] - number_bbox[1]) / 2

            drawing.text((text_x, text_y), number_text, fill="white", font=font)

            if parking_space_states[row, parking_space] == 1:
                car_x = center_x
                car_y = center_y + (font_size // 2 if row % 2 == 0 else -font_size // 2)

                car = Image.open("imgs/car.png").convert("RGBA")
                car = car.resize((car_width, car_height))

                if row % 2 != 0:
                    car = car.rotate(180)

                image.paste(car, (car_x - car_width // 2, car_y - car_height // 2), car)

    # Asegurarse de que la carpeta "slotParking" exista
    if not os.path.exists("slotParking"):
        os.makedirs("slotParking")

    # Guardar la imagen en la carpeta "slotParking"
    image.save(os.path.join("slotParking", "parking_result.png"), format="png")

def update_parking_states_from_csv(csv_mensajes_filename, parking_space_states):
    # Define los encabezados y tipos de datos
    columnas = ["Numero de Parqueo", "Estado del Parqueo", "Hora y Fecha"]
    tipos_de_datos = {"Numero de Parqueo": str, "Estado del Parqueo": int, "Hora y Fecha": str}

    # Lee el CSV con los encabezados y tipos de datos
    df = pd.read_csv(csv_mensajes_filename, header=0, names=columnas, dtype=tipos_de_datos)

    for index, row in df.iterrows():
        parking_spot = row[0]
        state = row[1]
        
        # Extraer el número del parqueo
        spot_number = int(parking_spot[1:])
        
        # Convertir el estado a entero
        state = int(state)
        
        # Verificar si el estado ha cambiado antes de actualizar
        if parking_space_states[(spot_number - 1) // parking_spaces_per_row, (spot_number - 1) % parking_spaces_per_row] != state:
            parking_space_states[(spot_number - 1) // parking_spaces_per_row, (spot_number - 1) % parking_spaces_per_row] = state
            print(f"Estado del parqueo {parking_spot} actualizado a {state}")


# Parámetros para el estacionamiento
rows = 5
parking_spaces_per_row = 10
parking_space_width = 100
parking_space_length = 200
space_between_rows = 100

# Inicializar el arreglo parking_space_states
parking_space_states = np.zeros((rows, parking_spaces_per_row), dtype=int)

# Llamar a la función para actualizar el arreglo desde el CSV
update_parking_states_from_csv(csv_mensajes_filename, parking_space_states)

# Llamar a la función para dibujar el estacionamiento
draw_parking_lot(rows, parking_spaces_per_row, parking_space_width, parking_space_length, space_between_rows, parking_space_states)

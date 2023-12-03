from pathlib import Path
import pyautogui
import numpy as np
import PIL.ImageOps
from numpy.random import uniform
from time import sleep, time
import soundcard as sc
import soundfile as sf
import matplotlib.pyplot as plt
import cv2
import sys

from PIL import Image
from PIL import ImageEnhance

import pytesseract
import re


SPEAKER_ID = None  # speaker to listen to for fish sound
SOUND_THRESH = 0.002  # sound threshold for catching fish.
OUTPUT_FOLDER = Path(r"temp")  # where to save outputs (images/audio plots) for debugging
PIX_X, PIX_Y = 2560, 1369  # size of screen in pixels
SEC = 1
SAMPLE_RATE = 48000  # audio sample rate
WAIT_PARAMETER = 2  # parameter passed to exponential distribution to sample wait time in seconds

KEY_LOOKUP = {
    "Interact": "8",
    "Left": "a",
    "Right": "d",
    "Fish": "9",
    "Oversized Bobber": "0",
    "Esc": "Escape",
    "Enter": "Enter"
}

pix_x, pix_y = PIX_X, PIX_Y

w = 800
h = 400
x = pix_x / 2 - w / 2
y = -150 + pix_y / 2 - h / 2


def save_img(filename: str, img: np.array):
    """
    Save image to output folder
    """
    if isinstance(img, PIL.Image.Image):
        img.save(OUTPUT_FOLDER / filename)
    else:
        cv2.imwrite(str(OUTPUT_FOLDER / filename), img)


def get_fishing_zone_and_bait_coords():
    """
    Screen shot the fishing zone, process the image and infer the bait by using the part of the red channel of the
    image with the most brightness
    """
    img = Image.open(OUTPUT_FOLDER / "status_cursor.png")
    img = np.array(img)
    img_raw = img.copy()

    img[:, :, 1] = 0
    img[:, :, 2] = 0

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray_blurred = cv2.blur(img_gray, (20, 20))
    img_gray_blurred_for_display = \
        cv2.normalize(img_gray_blurred, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(img_gray_blurred)
    cv2.circle(img_raw, max_loc, 5, 255, 2)
    cv2.circle(img_gray_blurred_for_display, max_loc, 5, 255, 2)


    save_img(f"status_2.png", img_raw[:, :, ::-1])
    save_img(f"status_blurred_2.png", img_gray_blurred_for_display)


def get_fishing_zone_and_bait_coords_v2():
    img = Image.open(OUTPUT_FOLDER / "status_cursor.png")
    img = np.array(img)
    img_raw = img.copy()

    img[:, :, 1] = 0
    img[:, :, 2] = 0

    # Extract the red channel
    red_channel = img[:, :, 0]

    # Invert the red channel to work with least brightness instead of most brightness
    inverted_red_channel = 255 - red_channel

    # Apply blurring to the inverted red channel
    inverted_red_blurred = cv2.blur(inverted_red_channel, (20, 20))

    # Normalize for display
    inverted_red_blurred_for_display = \
        cv2.normalize(inverted_red_blurred, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

    # Find the location with the minimum brightness
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(inverted_red_blurred)

    # Draw circles on the original and blurred images
    cv2.circle(img_raw, min_loc, 5, 255, 2)
    cv2.circle(inverted_red_blurred_for_display, min_loc, 5, 255, 2)
    
    save_img(f"status_2.png", img_raw[:, :, ::-1])
    save_img(f"status_blurred_2.png", inverted_red_blurred_for_display)


def get_fishing_zone_and_bait_coords_v3():
    img = Image.open(OUTPUT_FOLDER / "test2.png")
    img = np.array(img)
    img_raw = img.copy()

    # Calculate the dimensions of the square
    image_height, image_width, _ = img.shape
    square_width = image_width // 5.5
    square_height = image_height // 4.5
    
    # square_x = (img_width // 2) - (square_width // 2)
    # square_y = (img_height // 2) - (1.5 * square_height)

    # Calculate the position of the top-left corner of the square
    top_left_x = (image_width - square_width) // 2
    top_left_y = (image_height - square_height) // 2
    
    top_left_x = int((image_width // 2) - (square_width // 2))
    top_left_y = int((image_height // 2) - (1.2 * square_height))

    # Calculate the position of the bottom-right corner of the square
    bottom_right_x = int(top_left_x + square_width)
    bottom_right_y = int(top_left_y + square_height + (square_height // 7))

    print((top_left_x, top_left_y), (bottom_right_x, bottom_right_y))

    # Draw the thick red square
    cv2.rectangle(img_raw, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), -1)
    save_img(f"status_2.png", img_raw[:, :, ::-1])
    

def wow_queue_alert():
    """
    Watch your Wow Classic queue and alert you when your queue is nearly up! 
    It uses image recognition to examine screenshots taken periodically while your queue is showing on your screen.
    """
    img = Image.open(OUTPUT_FOLDER / "queue.png")
    # width, height = img.size
    # img = img.crop((width*.3, height*.3, width*.7, height*.6))
    img = img.point(lambda p: p > 128 and 255)
    img = ImageEnhance.Color(img).enhance(0)
    save_img(f"wow_queue_alert.png", img)
    
    imgdata = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    print(imgdata['text'])
    # imgtext = ' '.join([x for i,x in enumerate(imgdata['text']) if int(imgdata['conf'][i]) >= 70])
    # imgtime = re.search(r'time[^\d+]*(\d+)', imgtext).group(1)
    
    # print(imgtext)


def modify_image():
    import pytesseract
    import cv2
    import random

    # Carga la imagen
    image = Image.open(OUTPUT_FOLDER / "queue.png")
    image = image.point(lambda p: p > 128 and 255)
    image = ImageEnhance.Color(image).enhance(0)

    # Detecta el texto en la imagen
    text = pytesseract.image_to_string(image)

    # Crea una lista de palabras
    words = text.split()

    # Inicializa un diccionario para almacenar los colores de las palabras
    colors = {}
    
    print(words)

    # Itera sobre las palabras
    for word in words:
        # Obtiene un color aleatorio
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Almacena el color en el diccionario
        colors[word] = color

    # Itera sobre las palabras nuevamente
    for word in words:
        # Encuentra la posición de la palabra en la imagen
        (x, y, w, h) = cv2.boundingRect(cv2.imread(f"{OUTPUT_FOLDER}/queue.png", cv2.IMREAD_COLOR))


        "queue_mod.png"
        # Dibuja la palabra en la imagen con el color correspondiente
        cv2.putText(image, word, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, colors[word], 2)

        save_img(f"test_image.png", image)



modify_image()
from src.fishing import screenshot as ss
from src.fishing import config
import pyautogui
import numpy as np
from numpy.random import uniform
from time import sleep
import soundcard as sc
import soundfile as sf
import matplotlib.pyplot as plt
import cv2

pix_x, pix_y = 2560, 1080


w = 250
h = 250
x = pix_x / 2 - w / 2
y = -100 + pix_y / 2 - h / 2


def hold_key(keybind, seconds=1.00):
    key = config.KEY_LOOKUP[keybind]
    print(f"Action: {keybind} -> {key} for {seconds:.2f} seconds.")
    pyautogui.keyDown(key)
    sleep(seconds)
    pyautogui.keyUp(key)


def move_cursor_to_bait(j):
    _, coords = get_img(j)
    mouse_x = x + coords[0]
    mouse_y = y + coords[1]
    print(f"{j} moving cursor to bait @ {mouse_x, mouse_y} ...")
    pyautogui.moveTo(mouse_x, mouse_y, uniform(0.2, 0.7), pyautogui.easeOutQuad)


def get_sound(i):
    SAMPLE_RATE = 48000  # [Hz]. sampling rate.
    SEC = 1

    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(
            samplerate=SAMPLE_RATE) as mic:
        # record audio with loopback from default speaker.
        data = mic.record(numframes=SAMPLE_RATE * SEC)

        mean = sum(np.absolute(data)) / len(data)
        mean = mean[0]
        caught_fish = True if mean > 0.001 else False
        print(f"{i} fish volume = {mean:9.5f} --> catch = {caught_fish}")
        plt.plot(data)
        plt.savefig(config.OUTPUT_FOLDER / f"signal_{i}.jpg")
        plt.close()

        filename = config.OUTPUT_FOLDER / f"sound_{i}.wav"
        # change "data=data[:, 0]" to "data=data", if you would like to write audio as multiple-channels.
        sf.write(file=filename, data=data[:, 0], samplerate=SAMPLE_RATE)
    return caught_fish


def get_img(i):
    img = pyautogui.screenshot(region=(x, y, w, h))
    img = np.array(img)

    img[:, :, 1] = 0
    img[:, :, 2] = 0

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray_blurred = cv2.blur(img_gray, (20, 20))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(img_gray_blurred)
    cv2.circle(img_gray, max_loc, 5, 255, 2)

    ss.save_img(f"status_{i}.png", img+40)
    ss.save_img(f"status_blurred_{i}.png", img_gray+40)

    return img, max_loc


def countdown_timer():
    # Countdown timer
    print("Starting to fish. Click on Warcraft window ...", end="", flush=True)
    for i in range(0, 1):
        print(".", end="", flush=True)
        sleep(1)
    print("Go")


def fish():
    countdown_timer()
    ss.setup()
    counter = 1
    while True:
        if counter % 150 == 0:
            hold_key("Oversized Bobber")
        print(f"Fish iteration = {counter}")
        hold_key("Fish", uniform(0.9, 1.1))
        sleep(uniform(0.0, 0.2))
        move_cursor_to_bait(0)
        for i in range(8):
            hear_fish_sound = get_sound(i)
            if hear_fish_sound:
                pyautogui.click(button='right')
                print("Fish caught!!!")
                sleep(1)
                break
            sleep(1)
        counter += 1


if __name__ == "__main__":
    fish()

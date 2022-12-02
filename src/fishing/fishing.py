from src.fishing import screenshot as ss
from src.fishing import config
import pyautogui
import numpy as np
from time import sleep
import soundcard as sc
import soundfile as sf
import matplotlib.pyplot as plt
import cv2

keybind = "9"
pix_x, pix_y = 2560, 1080

w = 250
h = 250
x = pix_x / 2 - w / 2
y = pix_y / 2 - h / 2


def throw_line():
    print("Throwing line...")
    pyautogui.keyDown(keybind)
    sleep(1)
    pyautogui.keyUp(keybind)


def move_cursor_to_bait(j):
    _, coords = get_img(j)
    mouse_x = x + coords[0]
    mouse_y = y + coords[1]
    print(f"{j} moving cursor to bait {coords} - {mouse_x, mouse_y} ...")
    pyautogui.moveTo(mouse_x, mouse_y)


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
        print(f"{i} mean amplitude = {mean} --> fish caught sound = {caught_fish}")
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

    # remove character  which we do not want to detect
    # pad_x = 15
    # pad_y = 15
    # cx = int(w / 2)
    # cy = int(h / 2)
    # img_2[
    # cy - pad_y:cy + pad_y,
    # cx - pad_x:cx + pad_x,
    # ] = 0.0
    # ss.save_img(f"status_2_{i}.png", img)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray_blurred = cv2.blur(img_gray, (4, 4))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(img_gray_blurred)
    cv2.circle(img_gray, max_loc, 5, 255, 2)

    ss.save_img(f"status_{i}.png", img)
    ss.save_img(f"status_blurred_{i}.png", img_gray)

    return img, max_loc


if __name__ == "__main__":
    ss.setup()
    while True:
        throw_line()
        sleep(0.1)
        move_cursor_to_bait(0)
        for i in range(10):
            caught_fish = get_sound(i)
            if caught_fish:
                pyautogui.click(button='right')
                print("Fish caught!!!")
                sleep(1)
                break

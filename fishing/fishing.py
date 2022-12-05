from . import screenshot as ss
from . import config
import pyautogui
import numpy as np
from numpy.random import uniform
from time import sleep
import soundcard as sc
import soundfile as sf
import matplotlib.pyplot as plt
import cv2

pix_x, pix_y = config.PIX_X, config.PIX_Y

w = 250
h = 250
x = pix_x / 2 - w / 2
y = -100 + pix_y / 2 - h / 2


def randomly_turn():
    if uniform() < 0.1:
        amount = uniform(0.0005, 0.001)
        hold_key("Left", amount)
        sleep(1.0)
        hold_key("Right", amount)
        sleep(1.0)


def hold_key(keybind, seconds=1.00):
    key = config.KEY_LOOKUP[keybind]
    print(f"Action: {keybind} -> {key} for {seconds:.4f} seconds.")
    pyautogui.keyDown(key)
    sleep(seconds)
    pyautogui.keyUp(key)


def get_sound(i):

    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(
            samplerate=config.SAMPLE_RATE) as mic:
        # record audio with loopback from default speaker.
        data = mic.record(numframes=config.SAMPLE_RATE * config.SEC)

        mean = sum(np.absolute(data)) / len(data)
        mean = mean[0]
        caught_fish = True if mean > 0.002 else False
        print(f"{i} fish volume = {mean:9.5f} --> catch = {caught_fish}")
        plt.figure(figsize=(5, 1))
        plt.plot(data)
        plt.ylim(-0.12, 0.12)
        plt.title(f"Last {config.SEC} second(s) of audio", size=7)
        plt.savefig(config.OUTPUT_FOLDER / f"audio_signal_{i}.png", bbox_inches='tight')
        plt.savefig(config.OUTPUT_FOLDER / f"audio_signal.png", bbox_inches='tight')
        plt.close()

        filename = config.OUTPUT_FOLDER / f"sound_{i}.wav"
        # change "data=data[:, 0]" to "data=data", if you would like to write audio as multiple-channels.
        sf.write(file=filename, data=data[:, 0], samplerate=config.SAMPLE_RATE)
    return caught_fish


def move_cursor_to_bait():
    img, coords = get_img()
    mouse_x = x + coords[0]
    mouse_y = y + coords[1]
    print(f"Moving cursor to bait @ {mouse_x, mouse_y} ...")
    pyautogui.moveTo(mouse_x, mouse_y, uniform(0.2, 0.7), pyautogui.easeOutQuad)

    img = pyautogui.screenshot(region=(x, y, w, h))
    img = np.array(img)
    ss.save_img(f"status_cursor.png", img[:, :, ::-1])


def get_img():
    img = pyautogui.screenshot(region=(x, y, w, h))
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

    ss.save_img(f"status.png", img_raw[:, :, ::-1])
    ss.save_img(f"status_blurred.png", img_gray_blurred_for_display)

    return img, max_loc


def wait():
    wait_time = np.random.exponential(config.WAIT_PARAMETER)
    print(f"Waiting for {wait_time:.3f} seconds ... ")
    sleep(wait_time)


def logout():
    print("Logging out")
    hold_key("Esc", 1.0)
    hold_key("Esc", 1.0)
    hold_key("Enter", 1.0)
    pyautogui.write(r'/logout', interval=uniform(0.03, 0.2))
    hold_key("Enter", 1.0)


def login():
    print("Logging in from character selection screen")
    hold_key("Enter", 1.0)


def setup():
    print(f"Creating folder '{config.OUTPUT_FOLDER}' (check images here to see fish zone for debugging)")
    if not config.OUTPUT_FOLDER.exists():
        config.OUTPUT_FOLDER.mkdir()

    # Countdown timer
    window = pyautogui.getWindowsWithTitle("World of Warcraft")[0]
    while not window.isActive:
        print("Please click on WoW window")
        print("", end="", flush=True)
        sleep(2)
    print("*"*100)
    print("Starting to fish...")


def fish():
    setup()
    counter = 0
    while True:
        print("\n")
        print("*"*10)
        print(f"Fish iteration = {counter}")
        hold_key("Fish", uniform(0.9, 1.1))  # throw fish line
        sleep(uniform(0.1, 0.3)) # wait to move cursor
        move_cursor_to_bait()
        for i in range(8):
            hear_fish_sound = get_sound(i)
            if hear_fish_sound:
                pyautogui.click(button='right')
                sleep(0.5)  # always wait at least 0.5 seconds to loot
                print("Fish caught!!!")
                wait()  # wait random amount of time after catching
                break
            sleep(0.8)  # wait between sounds
        counter += 1


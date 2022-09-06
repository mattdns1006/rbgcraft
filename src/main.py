import pyautogui
import pytesseract
import glob
import os
import numpy as np
import cv2
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import PIL.ImageOps
from time import sleep

ROOT_FOLDER = Path(__file__).parents[1].absolute()
OUTPUT_FOLDER = ROOT_FOLDER / "out"
if not OUTPUT_FOLDER.exists():
    OUTPUT_FOLDER.mkdir()

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"
DELAY_BETWEEN_COMMANDS = 0.00
pix_x, pix_y = 2560, 1080

KEY_LOOKUP = {
    "a": "Left",
    "d": "Right",
    "1": "Flame Shock",
    "2": "Lightning Bolt",
    "r": "Earth Shock"
}


def save_img(filename: str, img: np.array):
    if isinstance(img, PIL.Image.Image):
        img.save(OUTPUT_FOLDER / filename)
    else:
        cv2.imwrite(str(OUTPUT_FOLDER / filename), img)


def hold_key(key, seconds=1.00):
    if key in KEY_LOOKUP.keys():
        print(f"Action: {key} -> {KEY_LOOKUP[key]} for {seconds:.2f} seconds.")
    pyautogui.keyDown(key)
    sleep(seconds)
    pyautogui.keyUp(key)
    sleep(DELAY_BETWEEN_COMMANDS)


def turn_to_nameplate(i, debug: bool = True):
    """
    Look for RED nameplates
    """
    y_start = 0
    h = 500
    x_start = 550
    w = 2560 - 550*2
    middle = int(w/2)
    img = pyautogui.screenshot(region=(x_start, y_start, w, h))
    img = np.array(img)
    # there is red warning text in middle of screen (e.g. wrong direction) which we do not want to detect
    img[155:195, middle-100:middle+100] = 0.0

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    r = cv2.inRange(hsv, (0, 25, 25), (25, 255, 255))  # red
    r = cv2.blur(r, (17, 17))
    ret, r_t = cv2.threshold(r, 45, 255, 0)

    try:
        m = cv2.moments(r_t)
        cx = int(m["m10"] / m["m00"])

        off_center_pixels = cx - middle
        print(f"{i} - target found {off_center_pixels}")
        if cx > middle:
            hold_key("d", 0.05)
            hold_key("w", 0.05)
        else:
            hold_key("a", 0.05)
            hold_key("w", 0.05)

    except ZeroDivisionError:
        random_walk()

    if debug:
        img_save = np.vstack((hsv[:, :, 0], r, r_t))
        save_img(f"turn_{i}.png", img_save)

    return 0


def random_walk():
    print("Couldn't find red nameplate. Running for random amount")
    forward_time = np.random.uniform(1.5, 5.5)
    turn_time = np.random.uniform(0.0, 0.1)
    hold_key('w', forward_time)
    if np.random.uniform() < 0.5:
        hold_key('a', turn_time)
    else:
        hold_key('d', turn_time)


def get_hp(i, debug: bool = True):
    y_start = 56
    h = 17
    x_start = 165
    w = 24
    hp = np.array(pyautogui.screenshot(region=(x_start, y_start, w, h)))

    msk = cv2.inRange(hp, np.array([200, 200, 200]), np.array([255, 255, 255]))  # number is white
    msk[-1] = 0.0  # clean up where it meets mana bar
    krn = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3))
    dlt = cv2.dilate(msk, krn, iterations=1)
    thr = 255 - cv2.bitwise_and(dlt, msk)
    thr = cv2.blur(thr, (2, 2))
    text = pytesseract.image_to_string(thr, config="--psm 10")
    if debug:
        save_img(f"hp_{i}.png", thr)
    error_parsing = False
    try:
        hp = int(text.split("%")[0])
    except ValueError:
        hp = 100
        error_parsing = True
    print(f"Current hp = {hp}. Error ({error_parsing})")
    return hp


def get_info_screenshot(i, debug = True):

    w = 220
    h = 100
    x = (pix_x / 2) - 110
    y = 100
    img = pyautogui.screenshot(region=(x, y, w, h))
    r, _, _ = img.split()  # only need red
    thresh = 180
    r_bin = r.point(lambda p: 255 if p > thresh else 0)
    r_bin = PIL.ImageOps.invert(r_bin).convert('1')
    text = pytesseract.image_to_string(r_bin).lower()
    try:
        ImageDraw.Draw(r_bin).text((0, 0), text, "black")
    except UnicodeEncodeError:
        print("Couldn't add debug text to image")
    if debug:
        save_img(f"info_processed_{i}.png", r_bin)
    print(f"Text extracted for img {i} = '{text}'")
    print("--"*10)
    return text


def go():
    i = 0
    while True:
        pyautogui.press('1')
        text = get_info_screenshot(i, True)
        hold_key('2', 2.0)  # dps
        hp = get_hp(i, debug=True)
        if hp < 50:
            print("Low HP: healing")
            pyautogui.press('4')
            hold_key('3', 1.5)  # heals
        i += 1
        # jump1
        if np.random.uniform() < 0.10:
            pyautogui.press('space')
        while True:
            if ("far" in text) or ("range" in text):
                print("Target found. Moving forward...")
                hold_key('w', np.random.uniform(0.1, 0.5))
                turn_to_nameplate(i, True)
                text = get_info_screenshot(i)
            elif ("wrong" in text) or ("in front" in text):
                print("Facing wrong way...")
                hold_key('d', 0.2)
                text = get_info_screenshot(i)
            elif ("you have no" in text) or ("no target" in text) or ("invalid" in text):
                random_walk()
                turn_to_nameplate(0, True)
                pyautogui.press('Tab')
                text = get_info_screenshot(i)
            else:
                i += 1
                break


def countdown_timer():
    # Countdown timer
    print("Starting", end="", flush=True)
    for i in range(0, 3):
        print(".", end="", flush=True)
        sleep(1)
    print("Go")


def clear_temp():
    print("Removing image files...")
    for temp_file in glob.glob("*.png"):
        os.remove(temp_file)


def main():
    clear_temp()
    countdown_timer()
    go()


if __name__ == "__main__":
    main()

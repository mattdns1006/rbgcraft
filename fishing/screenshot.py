import pyautogui
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image, ImageOps
import PIL.ImageOps
import pytesseract
from fishing import config
import glob
import os

# nameplate config
y_start = 0
h = 500
x_start = 550
w = 2560 - 550*2

MIDDLE = int(w / 2)


def plot_histograms():
    print("Saving histograms...")
    for name, img in get_latest_images().items():
        plt.figure(figsize=(8, 4))
        plt.hist(img.flatten())
        fname = str(config.OUTPUT_FOLDER / f"hist_{name}.png")
        plt.savefig(fname)


def setup():

    print("Creating folders")
    if not config.OUTPUT_FOLDER.exists():
        config.OUTPUT_FOLDER.mkdir()

    print("Removing image files...")
    for temp_file in glob.glob(str(config.OUTPUT_FOLDER / "*.png")):
        os.remove(temp_file)


def get_status_img(i, w, h, x, y):


    img = pyautogui.screenshot(region=(x, y, w, h))
    r, _, _ = img.split()  # only need red
    thresh = 180
    r_bin = r.point(lambda p: 255 if p > thresh else 0)
    r_bin = PIL.ImageOps.invert(r_bin).convert('1')

    save_img(f"status_{i}.png", r_bin)
    return r_bin


def get_nameplate_img(i):
    """
    Look for colored nameplates
    """

    img = pyautogui.screenshot(region=(x_start, y_start, w, h))
    img = np.array(img)
    # there is red warning text in middle of screen (e.g. wrong direction) which we do not want to detect
    img[155:195, MIDDLE - 100:MIDDLE + 100] = 0.0

    img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    r = cv2.inRange(img_hsv, (140, 25, 25), (150, 255, 255))
    r_blur = cv2.blur(r, (19, 19))
    _, r_t = cv2.threshold(r, 55, 255, 0)

    save_img(f"img_{i}.png", img)
    save_img(f"debug_nameplate_{i}.png", np.vstack((img_hsv[:, :, 0], r, r_blur, r_t)))
    save_img(f"nameplate_{i}.png", r_t)
    return r_t


def save_img(filename: str, img: np.array):
    if isinstance(img, PIL.Image.Image):
        img.save(config.OUTPUT_FOLDER / filename)
    else:
        cv2.imwrite(str(config.OUTPUT_FOLDER / filename), img)


def get_latest_images():
    latest_files = {}
    for prefix in ["nameplate", "status", "hp"]:
        files = glob.glob(str(config.OUTPUT_FOLDER / f"{prefix}_*.png"))
        latest = max(files, key=os.path.getctime)
        latest_files[prefix] = cv2.imread(latest, cv2.IMREAD_GRAYSCALE)
    return latest_files


def infer(i):
    img_status = get_status_img(i)
    status = infer_status(img_status)

    img_np = get_nameplate_img(i)
    cx = infer_nameplate_location(img_np)

    print(f"Status = '{status}'")

    print(f"cx = {cx}")
    hp = 100
    return status, hp, cx


def infer_status(img):
    text = pytesseract.image_to_string(img).lower()

    return text


def infer_hp(img):
    text = pytesseract.image_to_string(img, config="--psm 10")
    try:
        hp = int(text.split("%")[0])

    except ValueError:
        hp = 100
    return hp


def infer_nameplate_location(img):
    try:
        m = cv2.moments(img)
        cx = int(m["m10"] / m["m00"])
        off_center_pixels = cx - MIDDLE
    except ZeroDivisionError:
        off_center_pixels = None
    return off_center_pixels


import pyautogui
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image, ImageDraw, ImageOps
import PIL.ImageOps
import pytesseract
import config
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


def create_screenshots():
    print("Creating screenshots ... ")
    i = 0
    while True:
        get_status_img(i)
        get_hp_img(i)
        get_nameplate_img(i)
        i += 1
        if i > 10:
            i = 0  # reset
            # plot_histograms()


def get_status_img(i):

    w = 220
    h = 100
    x = (config.pix_x / 2) - 110
    y = 100
    img = pyautogui.screenshot(region=(x, y, w, h))
    r, _, _ = img.split()  # only need red
    thresh = 180
    r_bin = r.point(lambda p: 255 if p > thresh else 0)
    r_bin = PIL.ImageOps.invert(r_bin).convert('1')

    # save_img(f"status_{i}.png", r_bin)
    return r_bin


def get_hp_img(i):
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
    # save_img(f"hp_{i}.png", thr)
    return thr


def get_nameplate_img(i, debug: bool = True):
    """
    Look for RED nameplates
    """

    img = pyautogui.screenshot(region=(x_start, y_start, w, h))
    img = np.array(img)
    # there is red warning text in middle of screen (e.g. wrong direction) which we do not want to detect
    img[155:195, MIDDLE - 100:MIDDLE + 100] = 0.0

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    r = cv2.inRange(hsv, (0, 25, 25), (25, 255, 255))  # red
    r = cv2.blur(r, (19, 19))
    _, r_t = cv2.threshold(r, 55, 255, 0)

    # save_img(f"debug_nameplate_{i}.png", np.vstack((hsv[:, :, 0], r, r_t)))
    # save_img(f"nameplate_{i}.png", r_t)
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


def infer():
    img_status = get_status_img(0)
    status = infer_status(img_status)

    img_hp = get_hp_img(0)
    hp = infer_hp(img_hp)

    img_np = get_nameplate_img(0)
    cx = infer_nameplate_location(img_np)

    print(f"Status = '{status}'")
    print(f"Current hp = {hp}")
    print(f"cx = {cx}")

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


if __name__ == "__main__":
    setup()
    create_screenshots()

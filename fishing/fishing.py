from . import config
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

pix_x, pix_y = config.PIX_X, config.PIX_Y

w = 800
h = 800
x = pix_x / 2 - w / 2
y = -150 + pix_y / 2 - h / 2


def hold_key(keybind, seconds=1.00):
    """
    Holds key down for seconds according to config.KEY_LOOKUP
    """
    key = config.KEY_LOOKUP[keybind]
    print(f"Action: {keybind} -> {key} for {seconds:.4f} seconds.")
    pyautogui.keyDown(key)
    sleep(seconds)
    pyautogui.keyUp(key)


def get_sound(i):
    """
    Get speaker sound (defined in config.SPEAKER_ID) and use a significant sound (volume0 as inference that a fish has
    been caught, according to config.SOUND_THRESH
    """
    speaker_id = sc.default_speaker().name if config.SPEAKER_ID is None else config.SPEAKER_ID
    try:
        with sc.get_microphone(id=speaker_id, include_loopback=True).recorder(
                samplerate=config.SAMPLE_RATE) as mic:
            # record audio with loopback from default speaker.
            data = mic.record(numframes=config.SAMPLE_RATE * config.SEC)
    except IndexError:
        print(f"Couldn't find speaker device '{speaker_id}'. Available options are:")
        for speaker in sc.all_speakers():
            print(speaker.name)
        print("Set 'config.SPEAKER_ID' to one of the speakers listed above")
        sys.exit(1)

    # infer volume from record
    mean = sum(np.absolute(data)) / len(data)
    mean = mean[0]
    caught_fish = True if mean > config.SOUND_THRESH else False
    print(f"{i} catch = {caught_fish}: fish volume = {mean:9.5f}, speaker = '{speaker_id}'")

    # plot for show/debug
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


def save_img(filename: str, img: np.array):
    """
    Save image to output folder
    """
    if isinstance(img, PIL.Image.Image):
        img.save(config.OUTPUT_FOLDER / filename)
    else:
        cv2.imwrite(str(config.OUTPUT_FOLDER / filename), img)


def move_cursor_to_bait():
    """
    Move mouse cursor to fish bait using screenshot and coordinates
    """
    img, coords = get_fishing_zone_and_bait_coords()
    mouse_x = x + coords[0]
    mouse_y = y + coords[1]
    print(f"Moving cursor to bait @ {mouse_x, mouse_y} ...")
    pyautogui.moveTo(mouse_x, mouse_y, uniform(0.2, 0.7), pyautogui.easeOutQuad)

    img = pyautogui.screenshot(region=(x, y, w, h))
    img = np.array(img)
    save_img(f"status_cursor.jpg", img[:, :, ::-1])

def get_fishing_zone_and_bait_coords():
    
    sleep(2)
    """
    Screen shot the fishing zone, process the image and infer the bait by template matching a bait template
    """
    # Load the fishing zone image and the bait template
    img = pyautogui.screenshot(region=(x, y, w, h))
    img = np.array(img)
    img_raw = img.copy()

    img_path = r'D:\00_DEV\00.1-rgbcraft-1\TestingEnv\template.jpg'
    bait_template = cv2.imread(img_path)

    # Convert the images to grayscale
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bait_template_gray = cv2.cvtColor(bait_template, cv2.COLOR_BGR2GRAY)

    # Match the template to the fishing zone image
    match_result = cv2.matchTemplate(img_gray, bait_template_gray, cv2.TM_CCOEFF_NORMED)

    # Find the location of the maximum match value
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match_result)

    # Draw a rectangle around the bait location in the original image
    bait_w, bait_h = bait_template_gray.shape[::-1]
    top_left = max_loc
    bottom_right = (top_left[0] + bait_w, top_left[1] + bait_h)
    cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)

    # Get the central position of the rectangle
    xy_center = (top_left[0] + bait_w/2, top_left[1] + bait_h/2)

    # Save the original image and the blurred image
    save_img(f'status.jpg', img[:, :, ::-1])
    save_img(f'status_blurred.jpg', cv2.normalize(match_result, None, 0, 255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F))
    return img, xy_center


def wait():
    """
    Wait for a random amount of time using exponential rng distribution
    """
    wait_time = np.random.exponential(config.WAIT_PARAMETER)
    print(f"Waiting for {wait_time:.3f} seconds ... ")
    sleep(wait_time)


def logout():
    """
    Log character out of game into character selection screen
    """
    print("Logging out")
    hold_key("Esc", 1.0)
    hold_key("Esc", 1.0)
    hold_key("Enter", 1.0)
    pyautogui.write(r'/logout', interval=uniform(0.03, 0.2))
    hold_key("Enter", 1.0)


def login():
    """
    Login to game
    """
    print("Logging in from character selection screen")
    hold_key("Enter", 1.0)


def setup():
    """
    Create output folder for debugging
    Ensure correct window is active before fishing
    """
    print(f"Creating folder '{config.OUTPUT_FOLDER}' (check images here to see fish zone for debugging)")
    if not config.OUTPUT_FOLDER.exists():
        config.OUTPUT_FOLDER.mkdir()

    # Countdown timer
    window = pyautogui.getWindowsWithTitle("World of Warcraft")[0]
    while not window.isActive:
        print("Please click on WoW window")
        print("", end="", flush=True)
        sleep(2)
    print("*" * 100)
    print("Starting to fish...")


def fish(hours: float = 3.0 / 6):
    """
    Main wrapper function to fish.
    :param hours: number of hours (can be decimal) to run the program for. Defaults to 30 minutes.
    """
    setup()
    start_time = time()  # remember when we started
    seconds_to_run = hours * 60 * 60
    mins_to_run = seconds_to_run / 60
    print(f"Running for {mins_to_run:,} minutes")
    counter = 0
    not_elapsed_time = True
    while not_elapsed_time:
        elapsed_time = time() - start_time
        not_elapsed_time = elapsed_time < seconds_to_run
        print("\n")
        print("*" * 10)
        print(f"Fish iteration = {counter}, elapsed time = {elapsed_time / 60:.3f} mins (max = {mins_to_run:.3f})")
        hold_key("Fish", uniform(0.9, 1.1))  # throw fish line
        sleep(uniform(0.3, 0.5))  # wait to move cursor
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
    print("Finished fishing.")

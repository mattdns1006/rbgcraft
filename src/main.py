import pyautogui
import numpy as np
from time import sleep
from fishing import config
import datetime
import screenshot as ss
pyautogui.FAILSAFE = False
turner = {}


def turn_around():
    if "start" not in turner.keys():
        turner["start"] = datetime.datetime.now()
    start = turner["start"]
    end = datetime.datetime.now()
    if (end - start).seconds > 30:
        print("Turning around...")
        hold_key(key="a", seconds=0.70)
        turner["start"] = datetime.datetime.now()


def hold_key(key, seconds=1.00):
    if key in config.KEY_LOOKUP.keys():
        print(f"Action: {key} -> {config.KEY_LOOKUP[key]} for {seconds:.2f} seconds.")
    pyautogui.keyDown(key)
    sleep(seconds)
    pyautogui.keyUp(key)
    sleep(config.DELAY_BETWEEN_COMMANDS)


def turn_to_nameplate(cx, middle = ss.MIDDLE):

    if cx > middle:
        hold_key("d", 0.05)
        hold_key("w", 0.05)
    else:
        hold_key("a", 0.05)
        hold_key("w", 0.05)


def random_walk(right):
    print("Running ... ")
    forward_time = np.random.uniform(1.5, 3.5)
    turn_time = np.random.uniform(0.0, 0.1)
    hold_key('w', forward_time)
    if np.random.uniform() < 0.5 or right:
        hold_key('a', turn_time)
    else:
        hold_key('d', turn_time)
    # turn_around()


def go():
    i = 0
    no_target_count = 0
    while True:

        print("*"*100)
        hold_key('q', 0.00)
        hold_key('3', 0.00)
        hold_key('2', 0.00)
        hold_key('e', 0.00)

        status, hp, cx = ss.infer(i)
        i += 1
        if cx is not None:
            right = cx > ss.MIDDLE
        else:
            right = None
        if "target" in status:
            random_walk(right)
            print("Try to target...")
            no_target_count += 1
            pyautogui.press('Tab')
        elif ("far" in status) or ("range" in status):
            print(f"Moving to target far away (to right = {right})...")
            random_walk(right)
        elif ("wrong" in status) or ("front" in status) or ("facing" in status) or ("nee" in status):
            print("Facing wrong way...")
            hold_key('d', 0.2)
        elif ("you have no" in status) or ("target" in status) or ("nothing"):
            hold_key('d', 0.2)
            no_target_count += 1
            pyautogui.press('Tab')
        elif ("invalid" in status):
            hold_key('Tab', 0.2)
        elif ("mana" in status):
            pyautogui.press('4')
            sleep(4.0)
        elif ("not ready" in status):
            hold_key('2', 2.0)


def countdown_timer():
    # Countdown timer
    print("Starting", end="", flush=True)
    for i in range(0, 3):
        print(".", end="", flush=True)
        sleep(1)
    print("Go")


def main():
    ss.setup()
    countdown_timer()
    go()


if __name__ == "__main__":
    main()

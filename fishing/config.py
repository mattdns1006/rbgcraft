from pathlib import Path

SPEAKER_ID = None  # speaker to listen to for fish sound
SOUND_THRESH = 0.002  # sound threshold for catching fish.
OUTPUT_FOLDER = Path(r"C:\temp\rgbcraft")  # where to save outputs (images/audio plots) for debugging
PIX_X, PIX_Y = 2560, 1080  # size of screen in pixels
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

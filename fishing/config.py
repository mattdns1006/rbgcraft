from pathlib import Path

SPEAKER_ID = None  # speaker to listen to for fish sound
SOUND_THRESH = 0.002  # sound threshold for catching fish.
OUTPUT_FOLDER = Path(r"temp")  # where to save outputs (images/audio plots) for debugging
SEC = 1
HALF_SEC = 0.5
SAMPLE_RATE = 48000  # audio sample rate
WAIT_PARAMETER = 1  # parameter passed to exponential distribution to sample wait time in seconds

KEY_LOOKUP = {
    "Interact": "8",
    "Left": "a",
    "Right": "d",
    "Fish": "9",
    "Oversized Bobber": "0",
    "Esc": "Escape",
    "Enter": "Enter"
}

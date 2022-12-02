from pathlib import Path
import pytesseract

ROOT_FOLDER = Path(__file__).parents[2].absolute()
OUTPUT_FOLDER = ROOT_FOLDER / "out"


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"
DELAY_BETWEEN_COMMANDS = 0.00
pix_x, pix_y = 2560, 1080

KEY_LOOKUP = {
    "a": "Left",
    "d": "Right",
    "1": "Fel Rush",
    "q": "Fel Blade",
    "3": "Immolation Aura",
    "2": "Blade Dance",
    "e": "Chaos Strike"
}

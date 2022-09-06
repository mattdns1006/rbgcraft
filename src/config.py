from pathlib import Path
import pytesseract

ROOT_FOLDER = Path(__file__).parents[1].absolute()
OUTPUT_FOLDER = ROOT_FOLDER / "out"


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract"
DELAY_BETWEEN_COMMANDS = 0.00
pix_x, pix_y = 2560, 1080

KEY_LOOKUP = {
    "a": "Left",
    "d": "Right",
    "1": "Flame Shock",
    "2": "Lightning Bolt",
    "r": "Earth Shock",
    "f": "Stoneclaw"
}

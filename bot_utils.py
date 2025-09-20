# repos/cutgrass_autofarm/bot_utils.py

from datetime import datetime
from PIL import ImageGrab

def now():
    return datetime.now().strftime("[%H:%M:%S]")

def color_match(c1, c2, tolerance=20):
    return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

def get_pixel(x, y):
    try:
        img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
        return img.getpixel((0, 0))
    except Exception as e:
        print(f"{now()} ⚠️ Pixel read failed at ({x},{y}): {e}")
        return (0, 0, 0)

def log_event(tag, message):
    print(f"{now()} {tag} {message}")

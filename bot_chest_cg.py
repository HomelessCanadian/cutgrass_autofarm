# repos/cutgrass_autofarm/bot_chest_cg.py

import time
import random
from PIL import ImageGrab
from bot_utils import now


class ChestHandler:
    def __init__(self, injector, valid_auras, valid_types):
        self.injector = injector
        self.valid_auras = valid_auras
        self.valid_types = valid_types
        self.active = False
        self.allow_movement = False
        self.chest_mode = 2  # Default mode; set externally via -l flag
        self.key_px_tolerance = 10
        self.red_sat_threshold = 1.5
        self.aura_type = {
        "gold": (255, 215, 0),   # Big aura
        "blue": (0, 114, 255),   # Huge aura
    }
        self.chest_type = {
            "wood1": [(184, 158, 118), (150, 126, 94)],
            "wood2": [(216, 190, 143), (128, 97, 65)],
            "iron": [(102, 122, 130), (64, 78, 78)],
            "purple": [(132, 80, 158), (126, 73, 151)],
            "gold": [(210, 122, 19), (238, 186, 23)],
            "red": [(255, 0, 0)],
            "locked": [(59, 54, 43)],
        }

    def sync_flags(self, active, allow_movement): #Set active and movement permission flags
        self.active = active
        self.allow_movement = allow_movement
        
    # === Pixel & Input ===
    def get_pixel(self, x, y): 
        if not self.active:
            print(f"{now()} 🛑 Killswitch triggered before pixel grab—skipping ({x},{y})")
            return (0, 0, 0)

        try:
            img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
            pixel = img.getpixel((0, 0))

            # Normalize pixel to RGB tuple
            if isinstance(pixel, int):
                return (pixel, pixel, pixel)
            elif isinstance(pixel, tuple):
                if len(pixel) == 1:
                    return (pixel[0], pixel[0], pixel[0])
                elif len(pixel) == 4:
                    return pixel[:3]
                elif len(pixel) == 3:
                    return pixel
            return (0, 0, 0)

        except Exception as e:
            print(f"{now()} ⚠️ Pixel read failed at ({x},{y}): {e}")
            return (0, 0, 0)


    def color_match(self, c1, c2, tolerance=20):
        return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

    def click(self, x, y): #Simulate mouse click at (x, y) with slight jiggle
        jiggle_radius = 3
        for dx, dy in [(-jiggle_radius, 0), (jiggle_radius, 0), (0, -jiggle_radius), (0, jiggle_radius)]:
            self.injector.move(x + dx, y + dy)
            time.sleep(0.01)
        self.injector.move(x, y)
        time.sleep(0.05)
        self.injector.click(x, y)
        time.sleep(0.05)

    # === Chest UI ===
    def get_chest_ui_region(self):
        return [(x, y) for x in range(796, 796 + 95) for y in range(914, 914 + 35)]

    def detect_discard_button(self, mode="quick", tolerance=30):
        """
        Detects discard button presence using multiple strategies.
        mode = "quick" → key pixel check
        mode = "scan" → full region tone match
        mode = "saturation" → red dominance check
        mode = "darkened" → pixel dimness check
        """
        target_colors = [(255, 0, 7), (179, 0, 5)]

        if mode == "quick":
            coords = [(838, 906), (842, 910)]
            for x, y in coords:
                pixel = self.get_pixel(x, y)
                if any(self.color_match(pixel, tone, tolerance=10) for tone in target_colors):
                    print(f"{now()}🟥 Quick discard match at ({x},{y}) → {pixel}")
                    return True
            print(f"{now()}🕵️ Quick discard check failed")
            return False

        elif mode == "scan":
            region = [(x, y) for x in range(800, 890) for y in range(915, 945)]
            for x, y in region:
                if not self.active:
                    print(f"{now()} 🛑 Killswitch triggered during discard scan—exiting")
                    return False
                pixel = self.get_pixel(x, y)
                for target in target_colors:
                    if self.color_match(pixel, target, tolerance=self.key_px_tolerance):
                        print(f"{now()} 🎯 Discard button matched tone: {target}")
                        return True
            return False

        elif mode == "saturation":
            region = [(x, y) for x in range(800, 890) for y in range(915, 945)]
            saturation = self.red_saturation(region)
            print(f"{now()}🔬 Red saturation level: {saturation:.2f}")
            return saturation > self.red_sat_threshold  # Tune threshold as needed

        elif mode == "darkened":
            pixel = self.get_pixel(845, 930)
            result = pixel[0] < 100 and pixel[1] > 50 and pixel[2] > 50
            print(f"{now()}🧪 Darkened check → {pixel} → {result}")
            return result

        return False
    
    def wait_for_discard_absence(self, timeout=15, mode="quick"):
        start_time = time.time()
        while self.detect_discard_button(mode=mode):
            if time.time() - start_time > timeout:
                print(f"{now()}⏱️ Discard button still present after timeout")
                return False
            time.sleep(0.1)
        print(f"{now()}📴 Discard button gone")
        time.sleep(random.uniform(4, 5))
        return True

    # === Chest Logic ===
    
    def classify_chest_type(self, pixel):
        """Returns chest type string based on pixel color, or None."""
        for chest_name, tones in self.chest_type.items():
            if any(self.color_match(pixel, tone, tolerance=self.key_px_tolerance if chest_name == "locked" else 15) for tone in tones):
                return chest_name
        return None
    def classify_aura(self, pixel):
        for aura_name, tone in self.aura_type.items():
            if self.color_match(pixel, tone, tolerance=20):
                return aura_name
        return None

    def get_aura_and_type(self):
        aura_px = self.get_pixel(1015, 679)
        chest_px = self.get_pixel(960, 500)
        aura = self.classify_aura(aura_px)
        chest_type = self.classify_chest_type(chest_px)
        return aura or "none", chest_type or "unknown"

    def should_open_chest(self, chest_type_str, aura_str):
        mode = self.chest_mode

        if chest_type_str == "locked":
            print(f"{now()}🔒 Locked chest — always discard")
            return False

        if mode == 0:
            return False
        elif mode == 1:
            return True
        elif mode == 2:
            if chest_type_str in ["wood1", "wood2"] and aura_str not in ["gold", "blue"]:
                print(f"{now()}🪵 Wood chest without key aura — discard")
                return False
            return True
        elif mode == 3:
            if chest_type_str in ["wood1", "wood2", "iron"]:
                print(f"{now()}🪵🪙 Discarding wood or iron chest")
                return False
            return True
        elif mode == 4:
            if chest_type_str in ["purple", "gold", "red"]:
                return True
            print(f"{now()}📦 Chest below purple — discard")
            return False
        elif mode == 5:
            if chest_type_str == "gold":
                return True
            print(f"{now()}📦 Chest not gold — discard")
            return False
        elif mode == 6:
            # Remove red aura logic; only open by aura gold or blue if you want, otherwise remove mode 6 or redefine
            print(f"{now()}📦 Mode 6 no longer supports red aura - defaulting to discard")
            return False

        print(f"{now()}⚠️ Unknown chest mode: {mode} — defaulting to discard")
        return False

    def handle_chest(self):
        aura, chest_type = self.get_aura_and_type()
        if self.should_open_chest(chest_type, aura):
            print(f"{now()}✅ Opening chest: {chest_type} with aura {aura}")
            self.click(960, 500)  # or wherever the chest is
        else:
            print(f"{now()}❌ Discarding chest: {chest_type} with aura {aura}")
            self.click(838, 906)  # discard button


    def detect_death(self): # waits for respawn button to appear. if so, clicks it and starts the chest handler
        pixel = self.get_pixel(859, 679)
        if self.color_match(pixel, (195, 232, 255), tolerance=25):
            print(f"{now()}💀 Death detected at (859,679) → {pixel}")
            return True
        return False

    def handle_death(self):
        self.click(859, 679)
        print(f"{now()}💀 Respawned")
        self.allow_movement = False
        time.sleep(1.5)

        # Profiler: check discard button presence
        for i in range(10):
            present = self.detect_discard_button(mode="quick")
            print(f"{now()}🔍 Discard button check #{i+1}: {present}")
            if present:
                break
            time.sleep(0.5)


# repos/cutgrass_autofarm/bot_chest.py

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
        self.chest_mode = chest_mode = 2  # Default mode; set externally via -l flag
    def sync_flags(self, active, allow_movement):
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

    def click(self, x, y):
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

    def red_saturation(self, region):
        if not region:
            return 0

        # Get bounding box from region
        xs = [x for x, _ in region]
        ys = [y for _, y in region]
        x1, x2 = min(xs), max(xs) + 1
        y1, y2 = min(ys), max(ys) + 1

        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            pixels = img.load()
            width, height = img.size

            red_total = 0
            pixel_count = 0

            for x in range(width):
                for y in range(height):
                    r, g, b = pixels[x, y][:3]
                    red_total += r / max(g + b + 1, 1)  # Avoid divide-by-zero
                    pixel_count += 1

            return red_total / pixel_count if pixel_count else 0

        except Exception as e:
            print(f"{now()}⚠️ Saturation grab failed: {e}")
            return 0


    def discard_button_present(self):
        region = [(x, y) for x in range(800, 800 + 90) for y in range(915, 915 + 30)]
        target_colors = [(255, 0, 7), (179, 0, 5)]
        for x, y in region:
            if not self.active:
                print(f"{now()} 🛑 Killswitch triggered during discard scan—exiting")
                return False
            pixel = self.get_pixel(x, y)
            for target in target_colors:
                if self.color_match(pixel, target, tolerance=30):
                    print(f"{now()} 🎯 Discard button matched tone: {target}")
                    return True
        return False

    def discard_button_darkened(self):
        pixel = self.get_pixel(845, 930)
        return pixel[0] < 100 and pixel[1] > 50 and pixel[2] > 50


    def wait_for_discard_absence(self, timeout=15):
        start_time = time.time()
        while self.discard_button_present():
            if time.time() - start_time > timeout:
                print(f"{now()}⏱️ Discard button still present after timeout")
                return False
            time.sleep(0.1)
        print(f"{now()}📴 Discard button gone")
        time.sleep(random.uniform(4, 5))
        return True

    # === Chest Logic ===
    def get_aura_and_type(self):
        try:
            aura = self.get_pixel(1015, 679)
            chest_type = self.get_pixel(960, 500)

            # Normalize aura
            if not isinstance(aura, tuple) or len(aura) != 3:
                print(f"{now()} ❌ Aura pixel invalid: {aura} — forcing fallback")
                aura = (0, 0, 0)

            # Normalize chest type
            if not isinstance(chest_type, tuple) or len(chest_type) != 3:
                print(f"{now()} ❌ Chest type pixel invalid: {chest_type} — forcing fallback")
                chest_type = (0, 0, 0)

            return aura, chest_type

        except Exception as e:
            print(f"{now()} ❌ get_aura_and_type failed: {e}")
            return (0, 0, 0), (0, 0, 0)
    def is_locked_chest(self):
        pixel = self.get_pixel(1243, 505)
        return self.color_match(pixel, (59, 54, 43), tolerance=10)  # 3B362B


    def is_valid_aura(self, c):
        return any(self.color_match(c, val) for val in self.valid_auras.values())

    def is_valid_type(self, c):
        return any(self.color_match(c, val) for val in self.valid_types.values())

    def is_wood_chest(self):
        coords = [(904, 435), (914, 445)]
        tones = [
            (184, 158, 118),  # B89E76
            (150, 126, 94),   # 967E5E
            (216, 190, 143),  # D8BE8F
            (128, 97, 65),    # 806141
            (118, 88, 54),    # 765836
            (100, 74, 43)     # 644A2B
        ]
        for x, y in coords:
            pixel = self.get_pixel(x, y)
            if any(self.color_match(pixel, tone, tolerance=15) for tone in tones):
                return True
        return False
    
    def is_iron_chest(self, chest_type):
        iron_tones = [(102, 122, 130), (64, 78, 78)]  # 667A82, 404E4E
        for tone in iron_tones:
            if self.color_match(chest_type, tone, tolerance=15):
                print(f"{now()}🪙 Iron chest detected → {chest_type}")
                return True
        return False

    def is_purple_or_gold_chest(self):
        coords = [(941, 845), (951, 855)]
        tones = [
            (132, 80, 158),  # 84509E
            (126, 73, 151),  # 7E4997
            (210, 122, 19),  # D27A13
            (238, 186, 23)   # EEBA17
        ]
        for x, y in coords:
            pixel = self.get_pixel(x, y)
            if any(self.color_match(pixel, tone, tolerance=15) for tone in tones):
                return True
        return False

    def should_open_chest(self, chest_type, aura):
        mode = self.chest_mode  # Set externally via -l flag

        is_wood = self.is_wood_chest()
        is_locked = self.is_locked_chest()
        is_purple_or_gold = self.is_purple_or_gold_chest()
        is_red_aura = self.color_match(aura, (255, 0, 0), tolerance=20)  # Red aura
        is_gold = self.color_match(chest_type, (210, 122, 19), tolerance=15) or \
                self.color_match(chest_type, (238, 186, 23), tolerance=15)
        is_iron = self.color_match(chest_type, (102, 122, 130), tolerance=15) or \
                self.color_match(chest_type, (64, 78, 78), tolerance=15)

        if is_locked:
            print(f"{now()}🔒 Locked chest — always discard")
            return False

        if mode == 0:
            return False

        if mode == 1:
            return True

        if mode == 2:
            if is_wood and not self.is_valid_aura(aura):
                print(f"{now()}🪵 Wood chest without aura — discard")
                return False
            return True

        if mode == 3:
            if is_wood or is_iron:
                print(f"{now()}🪵🪙 Wood or iron chest — discard")
                return False
            return True

        if mode == 4:
            if is_purple_or_gold:
                return True
            print(f"{now()}📦 Chest below purple — discard")
            return False

        if mode == 5:
            if is_gold or is_red_aura:
                return True
            print(f"{now()}📦 Chest not red/gold — discard")
            return False

        if mode == 6:
            if is_red_aura:
                return True
            print(f"{now()}📦 Chest without red aura — discard")
            return False

        print(f"{now()}⚠️ Unknown chest mode: {mode} — defaulting to discard")
        return False

    def is_discard_button_present(self):
        coords = [(838, 906), (842, 910)]
        discard_colors = [(255, 0, 7), (179, 0, 5)]  # FF0007, B30005

        for x, y in coords:
            pixel = self.get_pixel(x, y)
            if any(self.color_match(pixel, tone, tolerance=10) for tone in discard_colors):
                print(f"{now()}🟥 Discard button detected at ({x},{y}) → {pixel}")
                return True

        print(f"{now()}🕵️ Discard button not detected at key pixels")
        return False


#     def handle_chest(self): #standard 
#         chest_count = 0
#         while self.discard_button_present():
#             if not self.active:
#                 print(f"{now()}🛑 Killswitch triggered during chest cycle—exiting")
#                 return
#             aura, chest_type = self.get_aura_and_type()
#             if self.is_valid_aura(aura) or self.is_valid_type(chest_type):
#                 self.click(950, 800)
#                 print(f"{now()}📦 Chest #{chest_count + 1} opened")
#                 red_ready = self.red_saturation(self.get_chest_ui_region()) > 0.8
#                 button_ready = not self.discard_button_darkened()
#                 pixel = self.get_pixel(1000, 850)
#                 if red_ready and button_ready:
#                     self.click(1000, 750)  # ✅ Always press single Open
#                     print(f"{now()}📦 Chest #{chest_count + 1} opened (forced single)")
#                 else:
#                     print(f"{now()}⚠️ Chest UI not ready or button dark—skipping click")
#                 self.wait_for_red_drop(threshold=0.95, timeout=15)
#             else:
#                 self.click(950, 950)
#                 print(f"{now()}🗑️ Chest #{chest_count + 1} discarded")
#             chest_count += 1
#             time.sleep(random.uniform(0.5, 1.0))
#         print(f"{now()}✅ Chest cycle complete after {chest_count} chests")
#         self.allow_movement = True
    def handle_chest(self):
        chest_count = 0
        print(f"{now()}📦 Starting chest cycle...")

        # Wait for discard button to appear
        timeout = time.time() + 5
        while not self.is_discard_button_present() and time.time() < timeout:
            print(f"{now()}⏳ Waiting for discard button...")
            time.sleep(0.5)

        while self.is_discard_button_present():
            print(f"{now()}🔍 Chest #{chest_count + 1} detected")

            if not self.active:
                print(f"{now()}🛑 Killswitch triggered during chest cycle—exiting")
                return

            # Check for locked chest
            if self.is_locked_chest():
                print(f"{now()}🔒 Locked chest detected — discarding")
                self.click(950, 950)
                print(f"{now()}🗑️ Chest #{chest_count + 1} discarded (locked)")
                chest_count += 1
                time.sleep(0.5)
                continue

            # Read aura and type
            aura, chest_type = self.get_aura_and_type()
            print(f"{now()}🎨 Aura: {aura}, Type: {chest_type}")

            if aura is None or chest_type is None:
                print(f"{now()}⚠️ Skipping chest due to invalid aura/type data.")
                time.sleep(1)
                continue

            # Decide based on farming mode
            if self.should_open_chest(chest_type, aura):
                print(f"{now()}✅ Chest #{chest_count + 1} is valid — opening")
                self.click(840, 840)
                print(f"{now()}📦 Chest #{chest_count + 1} opened (clicked 840,840)")
            else:
                print(f"{now()}❌ Chest #{chest_count + 1} discarded by mode {self.chest_mode}")
                self.click(950, 950)
                print(f"{now()}🗑️ Chest #{chest_count + 1} discarded")

            # Wait for chest UI to disappear
            print(f"{now()}⏳ Waiting for chest UI to disappear...")
            start_wait = time.time()
            while self.is_discard_button_present() and (time.time() - start_wait < 5):
                time.sleep(0.5)

            if self.is_discard_button_present():
                print(f"{now()}⚠️ Discard button still present after timeout. Attempting to force close.")
                self.click(950, 950)
            else:
                print(f"{now()}✅ Chest UI is gone. Proceeding.")

            chest_count += 1
            time.sleep(random.uniform(0.5, 1.0))

            if not self.active:
                print(f"{now()}🛑 Killswitch triggered during discard scan—exiting")
                return

        print(f"{now()}✅ Chest cycle complete after {chest_count} chests")
        self.allow_movement = True


    def detect_death(self):
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
            present = self.is_discard_button_present()
            print(f"{now()}🔍 Discard button check #{i+1}: {present}")
            if present:
                break
            time.sleep(0.5)

    def check_zone(self):
        try:
            zone_color = self.get_pixel(140, 115)
        except Exception as e:
            print(f"{now()}⚠️ Zone pixel read failed: {e}")
            return False

        if self.color_match(zone_color, (78, 50, 43)):
            print(f"{now()}↪️ Rejoining play area")
            self.hold_key('w', 10)
            return False
        elif self.color_match(zone_color, (220, 198, 165)):
            print(f"{now()}🧭 Zone confirmed")
            return True
        else:
            print(f"{now()}❓ Unknown zone color: {zone_color}")
            return False

    def hold_key(self, key, duration):
        import keyboard
        keyboard.press(key)
        time.sleep(duration)
        keyboard.release(key)

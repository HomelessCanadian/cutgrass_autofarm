import pyautogui
import time
import random
from PIL import ImageGrab
import threading
import keyboard
from ctypes_handler import CtypesMouseInjector

class ClassI:
    def __init__(self):
        self.active = False
        self.shutdown = False
        self.last_move = time.time()
        self.move_interval = random.uniform(4, 50)
        self.duty_cycle = 10  # Default hold time in seconds
        self.injector = CtypesMouseInjector()


        keyboard.add_hotkey('-', self.decrease_duty_cycle)
        keyboard.add_hotkey('=', self.increase_duty_cycle)

        # Chest filter config
        self.valid_auras = {
            "yellow": (231, 196, 60),
            "blue": (59, 229, 198)
        }
        self.valid_types = {
            "purple": (61, 16, 86),
            "grey1": (121, 140, 145),
            "grey2": (61, 75, 75)
        }

        # Start listeners
        threading.Thread(target=self.killswitch_listener, daemon=True).start()
        keyboard.add_hotkey('[', self.toggle_bot)

    def get_chest_ui_region(self):
        return [(x, y) for x in range(796, 796 + 95) for y in range(914, 914 + 35)]

    def get_pixel(self, x, y):
        return ImageGrab.grab().getpixel((x, y))

    def color_match(self, c1, c2, tolerance=20):
        return all(abs(a - b) <= tolerance for a, b in zip(c1, c2))

    def click(self, x, y):
        # Jiggle before click
        jiggle_radius = 3
        for dx, dy in [(-jiggle_radius, 0), (jiggle_radius, 0), (0, -jiggle_radius), (0, jiggle_radius)]:
            self.injector.move(x + dx, y + dy)
            time.sleep(0.01)
        self.injector.move(x, y)
        time.sleep(0.05)
        self.injector.click(x,y)
        time.sleep(0.05)


    def increase_duty_cycle(self):
        self.duty_cycle = min(60, self.duty_cycle + 1)
        print(f"🔺 Duty cycle: {self.duty_cycle}s")

    def decrease_duty_cycle(self):
        self.duty_cycle = max(1, self.duty_cycle - 1)
        print(f"🔻 Duty cycle: {self.duty_cycle}s")


#     def chest_ui_present(self):
#         region = [(x, y) for x in range(990, 1000) for y in range(840, 850)]
#         match_count = 0
#         volatile_count = 0
#         ref_pixel = self.get_pixel(995, 845)


        for x, y in region:
            pixel = self.get_pixel(x, y)
            if self.color_match(pixel, (220, 198, 165), tolerance=30):  # DCC6A5
                match_count += 1
            if not self.color_match(pixel, ref_pixel, tolerance=10):
                volatile_count += 1

        # If enough pixels match expected tone and aren't volatile, UI is likely present
        return match_count > 50 and volatile_count < 20

    def discard_button_present(self):
        pixel = self.get_pixel(950, 950)
        return self.color_match(pixel, (255, 0, 7), tolerance=25)
    
    def wait_for_discard_absence(self, timeout=15):
        start_time = time.time()
        while self.discard_button_present():
            if time.time() - start_time > timeout:
                print("⏱️ Discard button still present after timeout")
                return False
            time.sleep(0.1)
        print("📴 Discard button gone")
        time.sleep(random.uniform(4, 5))  # Buffer for animation or screen lag
        return True
    
    def get_chest_ui_region():
        return [(x, y) for x in range(796, 796 + 95) for y in range(914, 914 + 35)]

    def red_saturation(region, target_color=(255, 0, 7), tolerance=15):
        red_count = 0
        for x, y in region:
            pixel = self.get_pixel(x, y)
            if self.color_match(pixel, target_color, tolerance):
                red_count += 1
        return red_count / len(region)

    def wait_for_red_drop(self, threshold=0.99, timeout=15):
        region = self.get_chest_ui_region()

        start_time = time.time()

        while time.time() - start_time < timeout:
            saturation = self.red_saturation(region)
            print(f"🔴 Red saturation: {saturation:.3f}")
            if saturation < threshold:
                print("📴 Chest UI cleared (red dropped)")
                time.sleep(random.uniform(4, 5))
                return True
            time.sleep(0.2)

        print("⏱️ Red saturation timeout")
        return False

    def discard_button_present(self):
        pixel = self.get_pixel(950, 950)
        return self.color_match(pixel, (255, 0, 7), tolerance=15)

    def wait_for_discard_absence(self, timeout=15):
        start_time = time.time()
        while self.discard_button_present():
            if time.time() - start_time > timeout:
                print("⏱️ Discard button still present after timeout")
                return False
            time.sleep(0.1)
        print("📴 Discard button gone")
        time.sleep(random.uniform(4, 5))  # Buffer for animation or screen lag
        return True

    def walk_forward(self, duration=10):
        print(f"🚶 Walking forward for {duration}s")
        self.hold_key('w', duration)

    def hold_key(self, key, duration):
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)

    def detect_death(self):
        return self.color_match(self.get_pixel(859, 679), (195, 232, 255))

    def handle_death(self):
        self.click(859, 679)
        print("💀 Respawned")
        time.sleep(1)

    def get_aura_and_type(self):
        aura = self.get_pixel(1015, 679)
        chest_type = self.get_pixel(960, 500)
        return aura, chest_type

    def is_valid_aura(self, c):
        return any(self.color_match(c, val) for val in self.valid_auras.values())

    def is_valid_type(self, c):
        return any(self.color_match(c, val) for val in self.valid_types.values())

    def handle_chest(self):
        aura, chest_type = self.get_aura_and_type()
        if self.is_valid_aura(aura) or self.is_valid_type(chest_type):
            self.click(950, 800)  # Open chest
            print("📦 Chest opened")

            # Conditional click based on green pixel
            pixel = self.get_pixel(1000, 850)
            if self.color_match(pixel, (0, 255, 0), tolerance=40):
                self.click(1000, 850)
                print("✅ Green pixel detected → clicked 1000,850")
            else:
                self.click(1000, 750)
                print("❎ Not green → clicked 1000,750")

            # Wait for chest UI to close
            self.wait_for_red_drop(threshold=0.99, timeout=15)
            self.walk_forward(duration=10)


        else:
            self.click(950, 950)  # Discard
            print("🗑️ Chest discarded")

        time.sleep(0.5)

    def check_zone(self):
        zone_color = self.get_pixel(140, 115)
        if self.color_match(zone_color, (78, 50, 43)):  # 4E322B
            print("↪️ Rejoining play area")
            self.hold_key('w', 10)
        elif self.color_match(zone_color, (220, 198, 165)):  # DCC6A5
            return True
        else:
            return False
#     def random_movement(self):
#         key = random.choice(['w', 'a', 's', 'd'])
#         cycle_duration = 1.0  # 1000ms total cycle
#         press_time = cycle_duration * (self.duty_cycle_percent / 100.0)
#         release_time = cycle_duration - press_time
# 
#         print(f"🚶 {key.upper()} → {self.duty_cycle_percent}% duty ({press_time:.3f}s on / {release_time:.3f}s off)")
# 
#         pyautogui.keyDown(key)
#         time.sleep(press_time)
#         pyautogui.keyUp(key)
#         time.sleep(release_time)
    def random_movement(self):
        key = random.choice(['w', 'a', 's', 'd'])
        duration = random.uniform(4, 40)

        print(f"🚶 Holding {key.upper()} for {duration:.2f}s")
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)


    def killswitch_listener(self):
        while not self.shutdown:
            if keyboard.is_pressed('j') and keyboard.is_pressed('k') and keyboard.is_pressed('l'):
                self.shutdown = True
                self.active = False
                print("🛑 Killswitch activated")
            time.sleep(0.1)

    def toggle_bot(self):
        if not self.shutdown:
            self.active = not self.active
            print(f"🔁 Bot {'ENABLED' if self.active else 'DISABLED'}")

    def run(self):
        print("🎮 ClassI initialized. Press [ to toggle. J+K+L to kill.")
        while not self.shutdown:
            if not self.active:
                time.sleep(0.25)
                continue

            if self.detect_death():
                self.handle_death()

            self.handle_chest()

            if not self.check_zone():
                time.sleep(0.5)
                continue

            if time.time() - self.last_move > self.move_interval:
                self.random_movement()
                self.last_move = time.time()
                self.move_interval = random.uniform(4, 50)

            time.sleep(0.25)



# === Launch ===
if __name__ == "__main__":
    bot = ClassI()
    bot.run()

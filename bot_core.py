# bot_core
# repos/cutgrass_autofarm/bot_core.py
import time
import random
import threading
import keyboard
import pyautogui
from ctypes_handler import CtypesMouseInjector
from bot_utils import now
from bot_roam import BotRoam
from bot_chest import ChestHandler

class ClassI:
    def __init__(self):
        self.active = False
        self.shutdown = False
        self.last_move = time.time()
        self.move_interval = random.uniform(4, 50)
        self.duty_cycle = 10
        self.injector = CtypesMouseInjector()
        self.allow_movement = False
        

        # ✅ Define aura and type tones BEFORE using them
        self.valid_auras = {
            "yellow": (231, 196, 60),
            "blue": (59, 229, 198)
        }
        self.valid_types = {
            "purple": (61, 16, 86),
            "grey1": (121, 140, 145),
            "grey2": (61, 75, 75)
        }

        # ✅ Now safe to pass them into ChestHandler
        self.chest_handler = ChestHandler(
            injector=self.injector,
            valid_auras=self.valid_auras,
            valid_types=self.valid_types
        )
        self.roam = BotRoam()  # ✅ Must come before hotkeys
        self.chest_handler = ChestHandler(
            injector=self.injector,
            valid_auras=self.valid_auras,
            valid_types=self.valid_types
        )
        keyboard.add_hotkey('-', self.roam.decrease_duty_cycle)
        keyboard.add_hotkey('=', self.roam.increase_duty_cycle)
        keyboard.add_hotkey('[', self.toggle_bot)
        threading.Thread(target=self.killswitch_listener, daemon=True).start()


        self.valid_auras = {
            "yellow": (231, 196, 60),
            "blue": (59, 229, 198)
        }
        self.valid_types = {
            "purple": (61, 16, 86),
            "grey1": (121, 140, 145),
            "grey2": (61, 75, 75)
        }

    def killswitch_listener(self):
        while not self.shutdown:
            if keyboard.is_pressed('j') and keyboard.is_pressed('k') and keyboard.is_pressed('l'):
                self.shutdown = True
                self.active = False
                print(f"{now()}🛑 Killswitch activated")
            time.sleep(0.1)

    def toggle_bot(self):
        if not self.shutdown:
            self.active = not self.active
            self.chest_handler.sync_flags(self.active, self.allow_movement)
            print(f"{now()}🔁 Bot {'ENABLED' if self.active else 'DISABLED'}")


    def run(self):
        print(f"{now()}🔁 Loop started")
        death_check_interval = 2.5
        last_death_check = time.time()
        print(f"{now()} 🎮 ClassI initialized. Press [ to toggle. J+K+L to kill.")
        try:
            while not self.shutdown:
                # Movement logic
                if self.allow_movement and time.time() - self.last_move > self.move_interval:
                    print(f"{now()} 🚶 Movement triggered")
                    self.roam.random_movement()
                    self.last_move = time.time()
                    self.move_interval = random.uniform(4, 50)

                if not self.active:
                    time.sleep(0.25)
                    continue

                print(f"{now()} 🎮 CGfarm successfully loaded. (c) Copilot & Pank.")

                # Death check
                if time.time() - last_death_check >= death_check_interval:
                    last_death_check = time.time()
                    self.chest_handler.sync_flags(self.active, self.allow_movement)  # ✅ Sync flags
                    if self.chest_handler.detect_death():
                        self.chest_handler.handle_death()
                        self.chest_handler.handle_chest()
                        continue  # Skip movement until chest is handled

                # Zone check
                if not self.chest_handler.check_zone():
                    time.sleep(0.5)
                    continue

                time.sleep(0.25)
        except Exception as e:
            print(f"{now()} ❌ Fatal error: {e}")

            
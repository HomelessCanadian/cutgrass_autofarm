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
from bot_chest_cg import ChestHandler

class ClassI:
    def __init__(self, game="cg", afk_only=False):
        self.game = game
        self.afk_only = afk_only
        self.active = False
        self.shutdown = False
        self.last_move = time.time()
        self.move_interval = random.uniform(4, 50)
        self.duty_cycle = 10
        self.injector = CtypesMouseInjector()
        self.allow_movement = True
        self.roam = BotRoam()

        def hold_key(self, key, duration):
            keyboard.press(key)
            time.sleep(duration)
            keyboard.release(key)

        if not self.afk_only:
            self.chest_handler = ChestHandler(
                injector=self.injector,
                valid_auras={"yellow": (231, 196, 60), "blue": (59, 229, 198)},
                valid_types={"purple": (61, 16, 86), "grey1": (121, 140, 145), "grey2": (61, 75, 75)}
            )

        keyboard.add_hotkey('-', self.roam.decrease_duty_cycle)
        keyboard.add_hotkey('=', self.roam.increase_duty_cycle)
        keyboard.add_hotkey('[', self.toggle_bot)
        threading.Thread(target=self.killswitch_listener, daemon=True).start()

# 💃 AFK Dance Loop: Circle & Chest Tap Edition
# 🔁 Moves in a loop (W → WA → A → SA → S → SD → D → WD)
# 🎭 Varies timing per step, taps E occasionally for extra loot
# 🚫 Never reverses, never repeats—just vibes

    def afk_movement_loop(self):
        loop_sequence = ["w", "wa", "a", "sa", "s", "sd", "d", "wd"]
        step_index = 0
        chest_tap_counter = 0

        while not self.shutdown:
            if self.active and self.allow_movement and self.afk_only:
                direction = loop_sequence[step_index]
                hold_time = round(random.uniform(4, 12), 2)
                print(f"{now()}💃 Loop step: {direction.upper()} for {hold_time}s")

                for key in direction:
                    keyboard.press(key)
                time.sleep(hold_time)
                for key in direction:
                    keyboard.release(key)

                step_index = (step_index + 1) % len(loop_sequence)

                # Tap E every 3–6 steps for chest triggers
                chest_tap_counter += 1
                if chest_tap_counter >= random.randint(1, 1):
                    print(f"{now()}🎁 Tapping E for chest check")
                    keyboard.press("e")
                    time.sleep(0.1)
                    keyboard.release("e")
                    chest_tap_counter = 0
            else:
                time.sleep(0.25)



    def death_detection_loop(self):
        while not self.shutdown:
            if self.active and not self.afk_only:
                self.chest_handler.sync_flags(self.active, self.allow_movement)
                if self.chest_handler.detect_death():
                    self.chest_handler.handle_death()
                    self.chest_handler.handle_chest()
            time.sleep(2.5)


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
            if hasattr(self, "chest_handler") and self.chest_handler:
                self.chest_handler.sync_flags(self.active, self.allow_movement)
            print(f"{now()}🔁 Bot {'ENABLED' if self.active else 'DISABLED'}")



    def run(self):
        print(f"{now()}🔁 Loop started")
        print(f"{now()} 🎮 ClassI initialized. Press [ to toggle. J+K+L to kill.")
        print(f"{now()} 🎮 Game mode: {self.game} | AFK-only: {self.afk_only}")

        # Start AFK movement thread
        threading.Thread(target=self.afk_movement_loop, daemon=True).start()

        # Start death detection thread (only if chest logic is active)
        if not self.afk_only:
            threading.Thread(target=self.death_detection_loop, daemon=True).start()

        # Main loop just idles and watches for shutdown
        while not self.shutdown:
            time.sleep(0.25)

            
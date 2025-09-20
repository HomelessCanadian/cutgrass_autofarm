# repos/cutgrass_autofarm/bot_roam.py

import time
import random
import pyautogui
from bot_utils import now

class BotRoam:
    def __init__(self):
        self.duty_cycle = 10

    def random_movement(self):
        key = random.choice(['w', 'a', 's', 'd'])
        duration = random.uniform(4, 40)
        print(f"{now()}🚶 Holding {key.upper()} for {duration:.2f}s")
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)

    def walk_forward(self, duration=10):
        print(f"{now()}🚶 Walking forward for {duration}s")
        self.hold_key('w', duration)

    def hold_key(self, key, duration):
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)

    def increase_duty_cycle(self):
        self.duty_cycle = min(60, self.duty_cycle + 1)
        print(f"{now()}🔺 Duty cycle: {self.duty_cycle}s")

    def decrease_duty_cycle(self):
        self.duty_cycle = max(1, self.duty_cycle - 1)
        print(f"{now()}🔻 Duty cycle: {self.duty_cycle}s")

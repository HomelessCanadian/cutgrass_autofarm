***

# 🌾 Cutgrass Autofarm (beta)
**AFK chest farming, movement, and tactical resilience—now with AFK mode.**

***

## 🧩 Project Summary

Cutgrass Autofarm is a modular automation bot for the CG game environment.  
It supports both full-feature and AFK-only modes, enabling automated chest interaction, expressive AFK movement, and survival routines with hotkey control.

***

## 📦 Features

- **AFK Mode:** Bot cycles directional movement (W → WA → A → SA ect to form a circular pattern) with random timing to avoid idle triggers and fence traps.
- **Chest Automation:** Opens valid chests, discards junk, and taps E for extra loot.
- **Toggle Control:** `[`: Toggle bot on/off. `J + K + L`: Emergency shutdown (killswitch).
- **Threaded Architecture:** Movement, death detection, and chest handling run in parallel for responsive control.
- **Modular Design:** Easily extendable—add custom movement sequences and debug overlays.

***

## 🧰 Dependencies

- **Python 3.9+**
- `pyautogui`
- `keyboard`
- `Pillow`
- Standard library: `time`, `random`, `os`
- (Mouse injection via Python `ctypes` included)

Install dependencies:
```bash
pip install pyautogui pillow keyboard
```

***

## 🖥️ Usage

1. Download or clone the repository.
2. Start the CG game and position near chests.
3. Run the bot:
   ```bash
   python cgfarm.py --afk
   ```
   - AFK-only mode: Simulates movement and chest tapping; disables death detection/chest logic for pure idle farming.

4. Controls:
   - Press `[` to toggle the bot on/off.
   - Hold `J + K + L` for emergency killswitch.

***

## 🧭 Behavior Summary

- Detects chest types and auras with pixel scanning.
- Handles AFK movement and chest opening/discarding.
- Rejoins the play zone after death (full mode).
- Waits for UI signals before advancing.
- Randomizes movement keys and hold durations to mimic real play.

***

## 🧪 Notes

- Designed for expressive and reliable control, not stealth.
- Works best in windowed mode and with consistent UI scaling.
- May need adjustment for resolutions other than 1080p.
- Unexpected overlays/animals can interfere with pixel detection.

***

## 🐚 License

Licensed under **Shell License v1.0** (see Shell_License.md).

***

**Beta status:** Expect bugs and UI changes. Feedback and PRs welcome!

***

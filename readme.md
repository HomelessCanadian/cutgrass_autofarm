# 🌾 Cutgrass Autofarm  (beta)
**AFK chest farming with expressive control and tactical resilience.**

---

## 📦 What It Does

Cutgrass Autofarm automates chest interactions in-game using pixel detection and input injection. It opens valid chests, discards junk, walks forward when done, and loops randomized movement to simulate human activity. Built for reliability, not fragility.

---

## 🧰 Dependencies

Make sure these are installed before running:

- **Python 3.9+**
- `pyautogui` — for screen interaction  
- `Pillow` — for pixel sampling  
- `keyboard` — for hotkey toggles  
- `ctypes` — for HID-level input injection (included via native Python)  
- `time`, `random`, `os` — standard libraries

Install with:

```bash
pip install pyautogui pillow keyboard
```

---

## 🖥️ Setup & Usage

1. Clone or download the repo  
2. Launch the game and position your character near chests  
3. Run the script:

```bash
python cgfarm.py
```

4. Controls:
   - Press `[` to toggle the bot on/off  
   - Press `J + K + L` together to kill the bot instantly

---

## 🧭 Behavior Summary

- Detects chest type and aura via pixel scan  
- Rejoins play zone if death is detected
- Opens valid chests, discards others  (classes coming soon)
- Waits for red UI saturation to drop before walking forward  
- Walks forward for 10 seconds, then resumes AFK movement  
- Randomly holds `W/A/S/D` for 4–40 seconds to simulate activity  

---

### 🐚 License

This project is licensed under the **Shell License v1.0**. See Shell_License.md for more details.

---

## 🧪 Notes

- Designed for expressive control, not stealth  
- Works best in windowed mode with consistent UI scaling  
- May misfire if obstructed by overlays, guitars, or cats  
- Designed for 1080p resolution. May require scaling

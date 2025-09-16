import ctypes
import time

class CtypesMouseInjector:
    def __init__(self):
        self.INPUT_MOUSE = 0
        self.MOUSEEVENTF_MOVE = 0x0001
        self.MOUSEEVENTF_LEFTDOWN = 0x0002
        self.MOUSEEVENTF_LEFTUP = 0x0004
        self.MOUSEEVENTF_ABSOLUTE = 0x8000

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [("dx", ctypes.c_long),
                        ("dy", ctypes.c_long),
                        ("mouseData", ctypes.c_ulong),
                        ("dwFlags", ctypes.c_ulong),
                        ("time", ctypes.c_ulong),
                        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

        class INPUT(ctypes.Structure):
            _fields_ = [("type", ctypes.c_ulong),
                        ("mi", MOUSEINPUT)]

        self.INPUT = INPUT
        self.MOUSEINPUT = MOUSEINPUT

    def move(self, x, y):
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)

        abs_x = int(x * 65535 / screen_width)
        abs_y = int(y * 65535 / screen_height)

        self._send(abs_x, abs_y, self.MOUSEEVENTF_MOVE | self.MOUSEEVENTF_ABSOLUTE)

    def click(self, x, y):
        self.move(x, y)
        time.sleep(0.01)
        self._send_click(self.MOUSEEVENTF_LEFTDOWN)
        time.sleep(0.01)
        self._send_click(self.MOUSEEVENTF_LEFTUP)

    def _send_click(self, flags):
        extra = ctypes.c_ulong(0)
        mi = self.MOUSEINPUT(
            dx=0,
            dy=0,
            mouseData=0,
            dwFlags=flags,
            time=0,
            dwExtraInfo=ctypes.pointer(extra)
        )
        inp = self.INPUT(self.INPUT_MOUSE, mi)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))


    def _send(self, x, y, flags, absolute=True):
        extra = ctypes.c_ulong(0)
        mi = self.MOUSEINPUT(
            x if flags & self.MOUSEEVENTF_MOVE else 0,
            y if flags & self.MOUSEEVENTF_MOVE else 0,
            0,
            flags | (self.MOUSEEVENTF_ABSOLUTE if absolute else 0),
            0,
            ctypes.pointer(extra)
        )
        inp = self.INPUT(self.INPUT_MOUSE, mi)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

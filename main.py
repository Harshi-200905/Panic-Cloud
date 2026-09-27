import os
import sys
import time
import ctypes
import tkinter as tk
import keyboard

from detector import PersonDetector
from mascot import Mascot
from privacy import PrivacyController

# SINGLE INSTANCE ONLY
# Prevents cloud armies
# ============================================================

mutex = ctypes.windll.kernel32.CreateMutexW(
    None,
    False,
    "RunAwayPrivacyPetSingleInstance"
)

ERROR_ALREADY_EXISTS = 183

if (
    ctypes.windll.kernel32.GetLastError()
    == ERROR_ALREADY_EXISTS
):
    sys.exit()


# ============================================================
# ROOT
# ============================================================

root = tk.Tk()
root.withdraw()


# ============================================================
# PRIVACY CONTROLLER
# ============================================================

privacy = PrivacyController(
    root
)


# ============================================================
# CAMERA DETECTOR
# ============================================================

detector = PersonDetector()

camera_available = detector.start()


# ============================================================
# STATE
# ============================================================

current_mode = "panic"

protection_enabled = True

privacy_triggered_by_camera = False

last_intruder_time = 0

last_panic_time = 0


# How long someone must be gone before
# Blur / Hide restore.
RETURN_DELAY = 1.5


# Prevents Panic from repeating nonstop
# while someone is still standing behind you.
PANIC_COOLDOWN = 3.0


# ============================================================
# MODE
# ============================================================

def set_mode(mode):
    global current_mode

    current_mode = mode

    print(
        f"Mode: {mode.upper()}"
    )

    if "mascot" in globals():
        mascot.refresh_menu()

def toggle_protection():
    global protection_enabled

    protection_enabled = not protection_enabled

    if protection_enabled:
        print("Protection resumed.")

    else:
        emergency_restore()
        print("Protection paused.")

    if "mascot" in globals():
        mascot.refresh_menu()

# ============================================================
# MANUAL TEST MODE
# ============================================================

def test_mode():
    privacy.remember_active_vscode()

    print(
        f"Testing: {current_mode.upper()}"
    )


    success = privacy.activate(
        current_mode
    )


    if not success:
        return


    # Panic completes itself.
    # Blur and Hide need restoring afterward.
    if current_mode in (
        "blur",
        "hide"
    ):
        root.after(
            2200,
            privacy.restore
        )


# ============================================================
# EMERGENCY RESTORE
# ============================================================

def emergency_restore():
    global privacy_triggered_by_camera

    try:
        privacy.restore()

    except Exception as error:
        print(
            f"Emergency restore error: {error}"
        )


    privacy_triggered_by_camera = False


    print(
        "Emergency restore complete."
    )


# ============================================================
# PET VISIBILITY
# ============================================================

def toggle_pet():
    mascot.toggle_visibility()


# ============================================================
# RELOAD PET
# ============================================================

def reload_pet():
    emergency_restore()

    try:
        detector.stop()

    except Exception:
        pass


    try:
        keyboard.unhook_all_hotkeys()

    except Exception:
        pass


    python = sys.executable


    os.execl(
        python,
        python,
        *sys.argv
    )


# ============================================================
# QUIT APP
# ============================================================

def quit_app():
    emergency_restore()


    try:
        detector.stop()

    except Exception:
        pass


    try:
        keyboard.unhook_all_hotkeys()

    except Exception:
        pass


    root.destroy()


# ============================================================
# IMAGE PATH
# ============================================================

image_path = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "cloud.png"
)


# ============================================================
# MASCOT
# ============================================================

mascot = Mascot(
    root=root,
    image_path=image_path,
    get_mode=lambda: current_mode,
    set_mode=set_mode,
    get_protection=lambda: protection_enabled,
    toggle_protection=toggle_protection,
    test_mode=test_mode,
    hide_pet=toggle_pet,
    reload_pet=reload_pet,
    quit_app=quit_app
)

# ============================================================
# EMERGENCY RESTORE EVENT
# ============================================================

root.bind(
    "<<EmergencyRestore>>",
    lambda event: emergency_restore()
)


# ============================================================
# TRACK MOST RECENT VS CODE WINDOW
# ============================================================

def watch_vscode():
    privacy.remember_active_vscode()

    root.after(
        150,
        watch_vscode
    )


watch_vscode()


# ============================================================
# CAMERA WATCH
# ============================================================

def watch_camera():
    global privacy_triggered_by_camera
    global last_intruder_time
    global last_panic_time

    if not protection_enabled:
        root.after(
            250,
            watch_camera
        )

        return

    if not camera_available:
        root.after(
            1000,
            watch_camera
        )

        return


    try:
        face_count = (
            detector.get_face_count()
        )

    except Exception as error:

        print(
            f"Camera detection error: {error}"
        )

        root.after(
            1000,
            watch_camera
        )

        return


    # ========================================================
    # SECOND PERSON DETECTED
    # ========================================================

    if face_count >= 2:

        last_intruder_time = (
            time.time()
        )


        # ----------------------------------------------------
        # PANIC
        # ----------------------------------------------------

        if current_mode == "panic":

            now = time.time()


            if (
                now - last_panic_time
                >= PANIC_COOLDOWN
            ):

                privacy.remember_active_vscode()


                print(
                    f"Intruder detected: "
                    f"{face_count} faces"
                )


                success = privacy.activate(
                    "panic"
                )


                if success:
                    last_panic_time = now


        # ----------------------------------------------------
        # BLUR / HIDE
        # ----------------------------------------------------

        elif current_mode in (
            "blur",
            "hide"
        ):

            if not privacy_triggered_by_camera:

                privacy.remember_active_vscode()


                print(
                    f"Intruder detected: "
                    f"{face_count} faces"
                )


                success = privacy.activate(
                    current_mode
                )


                if success:
                    privacy_triggered_by_camera = True


    # ========================================================
    # PERSON LEAVES
    # ========================================================

    elif privacy_triggered_by_camera:

        safe_for = (
            time.time()
            - last_intruder_time
        )


        if safe_for >= RETURN_DELAY:

            privacy.restore()

            privacy_triggered_by_camera = False


            print(
                "Coast is clear."
            )


    # Check camera again
    root.after(
        120,
        watch_camera
    )


# ============================================================
# GLOBAL SHORTCUTS
# ============================================================

keyboard.add_hotkey(
    "ctrl+shift+space",
    lambda: root.after(
        0,
        toggle_pet
    )
)

keyboard.add_hotkey(
    "ctrl+shift+p",
    lambda: root.after(
        0,
        toggle_protection
    )
)

keyboard.add_hotkey(
    "alt+1",
    lambda: root.after(
        0,
        lambda: set_mode(
            "panic"
        )
    )
)


keyboard.add_hotkey(
    "alt+2",
    lambda: root.after(
        0,
        lambda: set_mode(
            "blur"
        )
    )
)


keyboard.add_hotkey(
    "alt+3",
    lambda: root.after(
        0,
        lambda: set_mode(
            "hide"
        )
    )
)


keyboard.add_hotkey(
    "ctrl+t",
    lambda: root.after(
        0,
        test_mode
    )
)


keyboard.add_hotkey(
    "esc",
    lambda: root.after(
        0,
        emergency_restore
    )
)


keyboard.add_hotkey(
    "ctrl+shift+r",
    lambda: root.after(
        0,
        reload_pet
    )
)


keyboard.add_hotkey(
    "ctrl+shift+q",
    lambda: root.after(
        0,
        quit_app
    )
)


# ============================================================
# START CAMERA WATCH
# ============================================================

watch_camera()


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()
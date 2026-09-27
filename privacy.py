import time
import random
import tkinter as tk

import win32gui
import win32con

from PIL import ImageGrab, ImageFilter, ImageTk


class PrivacyController:
    def __init__(self, root):
        self.root = root

        self.last_vscode = None
        self.protected_hwnd = None
        self.current_mode = None

        # Blur
        self.blur_overlay = None
        self.blur_photo = None

        # Panic
        self.panic_overlay = None
        self.panic_label = None
        self.panic_photo = None


    # ========================================================
    # ACTIVE VS CODE
    # ========================================================

    def remember_active_vscode(self):
        hwnd = win32gui.GetForegroundWindow()

        if not hwnd:
            return

        title = win32gui.GetWindowText(
            hwnd
        )

        if "Visual Studio Code" in title:
            self.last_vscode = hwnd


    # ========================================================
    # POSITION
    # ========================================================

    def get_position(self, hwnd):
        left, top, right, bottom = (
            win32gui.GetWindowRect(
                hwnd
            )
        )

        return {
            "x": left,
            "y": top,
            "width": right - left,
            "height": bottom - top
        }


    # ========================================================
    # ACTIVATE
    # ========================================================

    def activate(self, mode):
        hwnd = self.last_vscode

        if not hwnd:
            print(
                "Click into a VS Code window first."
            )

            return False


        if not win32gui.IsWindow(
            hwnd
        ):
            print(
                "VS Code window is no longer valid."
            )

            return False


        self.protected_hwnd = hwnd
        self.current_mode = mode


        try:

            if mode == "panic":
                self.panic(
                    hwnd
                )

            elif mode == "blur":
                self.blur(
                    hwnd
                )

            elif mode == "hide":
                self.hide(
                    hwnd
                )

            else:
                return False


            return True


        except Exception as error:

            print(
                f"Protection error: {error}"
            )

            self.restore()

            return False


    # ========================================================
    # PANIC
    # ========================================================

    def panic(self, hwnd):
        pos = self.get_position(
            hwnd
        )

        left = pos["x"]
        top = pos["y"]

        width = pos["width"]
        height = pos["height"]

        right = left + width
        bottom = top + height


        screenshot = ImageGrab.grab(
            bbox=(
                left,
                top,
                right,
                bottom
            )
        )


        transparent = "#ff00ff"

        self.panic_overlay = (
            tk.Toplevel(
                self.root
            )
        )

        self.panic_overlay.overrideredirect(
            True
        )

        self.panic_overlay.attributes(
            "-topmost",
            True
        )

        self.panic_overlay.configure(
            bg=transparent
        )

        try:
            self.panic_overlay.wm_attributes(
                "-transparentcolor",
                transparent
            )
        except Exception:
            pass


        screen_width = (
            self.root.winfo_screenwidth()
        )

        screen_height = (
            self.root.winfo_screenheight()
        )


        self.panic_overlay.geometry(
            f"{screen_width}x"
            f"{screen_height}+0+0"
        )


        self.panic_photo = (
            ImageTk.PhotoImage(
                screenshot
            )
        )


        self.panic_label = tk.Label(
            self.panic_overlay,
            image=self.panic_photo,
            bg=transparent,
            borderwidth=0
        )


        self.panic_label.place(
            x=left,
            y=top,
            width=width,
            height=height
        )


        self.panic_overlay.update()


        frames = 60

        for frame in range(
            frames
        ):

            if frame < 12:
                strength_x = 12
                strength_y = 8

            elif frame < 28:
                strength_x = 28
                strength_y = 18

            else:
                strength_x = 50
                strength_y = 30


            dx = random.randint(
                -strength_x,
                strength_x
            )

            dy = random.randint(
                -strength_y,
                strength_y
            )


            scale = random.uniform(
                0.985,
                1.015
            )


            new_width = int(
                width * scale
            )

            new_height = int(
                height * scale
            )


            x = (
                left
                + dx
                - (
                    new_width
                    - width
                ) // 2
            )

            y = (
                top
                + dy
                - (
                    new_height
                    - height
                ) // 2
            )


            self.panic_label.place(
                x=x,
                y=y,
                width=new_width,
                height=new_height
            )


            self.panic_overlay.update()


            time.sleep(
                0.012
            )


        self.remove_panic_overlay()

        self.current_mode = None


    # ========================================================
    # REMOVE PANIC
    # ========================================================

    def remove_panic_overlay(self):
        if self.panic_overlay:

            try:
                self.panic_overlay.destroy()
            except Exception:
                pass


        self.panic_overlay = None
        self.panic_label = None
        self.panic_photo = None


    # ========================================================
    # HIDE
    # ========================================================

    def hide(self, hwnd):
        win32gui.ShowWindow(
            hwnd,
            win32con.SW_HIDE
        )


    # ========================================================
    # BLUR
    # ========================================================

    def blur(self, hwnd):
        pos = self.get_position(
            hwnd
        )


        left = pos["x"]
        top = pos["y"]

        right = (
            left
            + pos["width"]
        )

        bottom = (
            top
            + pos["height"]
        )


        screenshot = ImageGrab.grab(
            bbox=(
                left,
                top,
                right,
                bottom
            )
        )


        screenshot = screenshot.filter(
            ImageFilter.GaussianBlur(
                28
            )
        )


        self.blur_overlay = tk.Toplevel(
            self.root
        )

        self.blur_overlay.overrideredirect(
            True
        )

        self.blur_overlay.attributes(
            "-topmost",
            True
        )

        self.blur_overlay.geometry(
            f"{pos['width']}x"
            f"{pos['height']}+"
            f"{left}+{top}"
        )


        self.blur_photo = (
            ImageTk.PhotoImage(
                screenshot
            )
        )


        label = tk.Label(
            self.blur_overlay,
            image=self.blur_photo,
            borderwidth=0
        )


        label.pack(
            fill="both",
            expand=True
        )


        self.blur_overlay.update()


    # ========================================================
    # RESTORE
    # ========================================================

    def restore(self):
        hwnd = self.protected_hwnd


        self.remove_panic_overlay()


        if self.blur_overlay:

            try:
                self.blur_overlay.destroy()
            except Exception:
                pass


        self.blur_overlay = None
        self.blur_photo = None


        if (
            hwnd
            and win32gui.IsWindow(hwnd)
            and self.current_mode == "hide"
        ):

            try:
                win32gui.ShowWindow(
                    hwnd,
                    win32con.SW_SHOW
                )

            except Exception as error:
                print(
                    f"Restore error: {error}"
                )


        self.current_mode = None
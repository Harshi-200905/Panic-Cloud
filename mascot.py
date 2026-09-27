import tkinter as tk

from PIL import Image, ImageTk


BG = "#202124"
TEXT = "#f1f3f4"
MUTED = "#aeb0b4"
SEPARATOR = "#3a3b3f"
BORDER = "#45474c"

CHECK = "✓"


class Mascot:
    def __init__(
        self,
        root,
        image_path,
        get_mode,
        set_mode,
        get_protection,
        toggle_protection,
        test_mode,
        hide_pet,
        reload_pet,
        quit_app
    ):
        self.root = root

        self.get_mode = get_mode
        self.set_mode_callback = set_mode

        self.get_protection = get_protection
        self.toggle_protection_callback = toggle_protection

        self.test_mode_callback = test_mode
        self.hide_pet_callback = hide_pet
        self.reload_pet_callback = reload_pet
        self.quit_app_callback = quit_app

        self.menu = None
        self.visible = True

        self.drag_start_x = 0
        self.drag_start_y = 0

        self.window_start_x = 0
        self.window_start_y = 0

        self.total_drag = 0


        # ====================================================
        # FLOATING CLOUD
        # ====================================================

        self.window = tk.Toplevel(
            self.root
        )

        self.window.overrideredirect(
            True
        )

        self.window.attributes(
            "-topmost",
            True
        )

        transparent = "#ff00ff"

        self.window.configure(
            bg=transparent
        )

        try:
            self.window.wm_attributes(
                "-transparentcolor",
                transparent
            )
        except Exception:
            pass


        # ====================================================
        # LOAD IMAGE
        # ====================================================

        image = Image.open(
            image_path
        ).convert("RGBA")

        bbox = image.getbbox()

        if bbox:
            image = image.crop(
                bbox
            )

        max_width = 115

        ratio = (
            max_width
            / image.width
        )

        new_height = int(
            image.height
            * ratio
        )

        image = image.resize(
            (
                max_width,
                new_height
            ),
            Image.Resampling.LANCZOS
        )

        self.photo = ImageTk.PhotoImage(
            image
        )

        self.label = tk.Label(
            self.window,
            image=self.photo,
            bg=transparent,
            borderwidth=0,
            cursor="hand2"
        )

        self.label.pack()

        self.window.geometry(
            "+70+170"
        )


        # ====================================================
        # CLICK / DRAG
        # ====================================================

        self.label.bind(
            "<ButtonPress-1>",
            self.start_drag
        )

        self.label.bind(
            "<B1-Motion>",
            self.drag
        )

        self.label.bind(
            "<ButtonRelease-1>",
            self.end_drag
        )


    # ========================================================
    # DRAGGING
    # ========================================================

    def start_drag(self, event):
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

        self.window_start_x = (
            self.window.winfo_x()
        )

        self.window_start_y = (
            self.window.winfo_y()
        )

        self.total_drag = 0


    def drag(self, event):
        dx = (
            event.x_root
            - self.drag_start_x
        )

        dy = (
            event.y_root
            - self.drag_start_y
        )

        self.total_drag = (
            abs(dx)
            + abs(dy)
        )

        new_x = (
            self.window_start_x
            + dx
        )

        new_y = (
            self.window_start_y
            + dy
        )

        self.window.geometry(
            f"+{new_x}+{new_y}"
        )

        # Move menu with cloud
        if self.menu:
            menu_x = (
                new_x
                + 10
            )

            menu_y = (
                new_y
                + self.window.winfo_height()
                + 6
            )

            self.menu.geometry(
                f"+{menu_x}+{menu_y}"
            )


    def end_drag(self, event):
        if self.total_drag < 8:
            self.toggle_menu()


    # ========================================================
    # PET VISIBILITY
    # ========================================================

    def toggle_visibility(self):
        if self.visible:

            self.window.withdraw()

            if self.menu:
                self.close_menu()

            self.visible = False

        else:

            self.window.deiconify()
            self.window.lift()

            self.visible = True


    # ========================================================
    # MENU
    # ========================================================

    def toggle_menu(self):
        if self.menu:
            self.close_menu()

        else:
            self.open_menu()


    def close_menu(self):
        if self.menu:
            try:
                self.menu.destroy()
            except Exception:
                pass

        self.menu = None


    def refresh_menu(self):
        if self.menu:
            self.close_menu()
            self.open_menu()


    def open_menu(self):
        self.menu = tk.Toplevel(
            self.root
        )

        self.menu.overrideredirect(
            True
        )

        self.menu.attributes(
            "-topmost",
            True
        )

        self.menu.configure(
            bg=BG
        )


        x = (
            self.window.winfo_x()
            + 10
        )

        y = (
            self.window.winfo_y()
            + self.window.winfo_height()
            + 6
        )

        self.menu.geometry(
            f"285x320+{x}+{y}"
        )


        outer = tk.Frame(
            self.menu,
            bg=BORDER,
            padx=1,
            pady=1
        )

        outer.pack(
            fill="both",
            expand=True
        )


        content = tk.Frame(
            outer,
            bg=BG
        )

        content.pack(
            fill="both",
            expand=True
        )


        header = tk.Label(
            content,
            text="Panic Cloud",
            fg=TEXT,
            bg=BG,
            font=(
                "Segoe UI",
                11,
                "bold"
            ),
            anchor="w"
        )

        header.pack(
            fill="x",
            padx=14,
            pady=(12, 7)
        )


        self.separator(
            content
        )


        mode_label = tk.Label(
            content,
            text="Mode",
            fg=MUTED,
            bg=BG,
            font=(
                "Segoe UI",
                9
            ),
            anchor="w"
        )

        mode_label.pack(
            fill="x",
            padx=14,
            pady=(8, 2)
        )


        self.add_mode_row(
            content,
            "Panic",
            "panic",
            "Alt+1"
        )

        self.add_mode_row(
            content,
            "Blur",
            "blur",
            "Alt+2"
        )

        self.add_mode_row(
            content,
            "Hide",
            "hide",
            "Alt+3"
        )


        self.separator(
            content
        )


        protection_text = (
            "Pause protection"
            if self.get_protection()
            else "Resume protection"
        )

        self.add_action_row(
            content,
            protection_text,
            "Ctrl+Shift+P",
            self.toggle_protection_callback
        )


        self.add_action_row(
            content,
            "Test mode",
            "Ctrl+T",
            self.test_mode_callback
        )

        self.add_action_row(
            content,
            "Hide / Show pet",
            "Ctrl+Shift+Space",
            self.hide_pet_callback
        )

        self.add_action_row(
            content,
            "Reload pet",
            "Ctrl+Shift+R",
            self.reload_pet_callback
        )


        self.separator(
            content
        )


        self.add_action_row(
            content,
            "Emergency restore",
            "Esc",
            self.emergency_restore
        )

        self.add_action_row(
            content,
            "Quit pet",
            "Ctrl+Shift+Q",
            self.quit_app_callback
        )


    # ========================================================
    # SEPARATOR
    # ========================================================

    def separator(self, parent):
        line = tk.Frame(
            parent,
            bg=SEPARATOR,
            height=1
        )

        line.pack(
            fill="x",
            padx=8,
            pady=5
        )


    # ========================================================
    # MODE ROW
    # ========================================================

    def add_mode_row(
        self,
        parent,
        text,
        value,
        shortcut
    ):
        selected = (
            self.get_mode()
            == value
        )

        prefix = (
            CHECK
            if selected
            else " "
        )


        row = tk.Frame(
            parent,
            bg=BG,
            cursor="hand2"
        )

        row.pack(
            fill="x",
            padx=5
        )


        left = tk.Label(
            row,
            text=f"{prefix}   {text}",
            fg=TEXT,
            bg=BG,
            font=(
                "Segoe UI",
                10
            ),
            anchor="w"
        )

        left.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 4),
            pady=6
        )


        right = tk.Label(
            row,
            text=shortcut,
            fg=MUTED,
            bg=BG,
            font=(
                "Segoe UI",
                9
            )
        )

        right.pack(
            side="right",
            padx=(4, 10)
        )


        def click(_=None):
            self.set_mode_callback(
                value
            )


        for widget in (
            row,
            left,
            right
        ):
            widget.bind(
                "<Button-1>",
                click
            )


    # ========================================================
    # ACTION ROW
    # ========================================================

    def add_action_row(
        self,
        parent,
        text,
        shortcut,
        command
    ):
        row = tk.Frame(
            parent,
            bg=BG,
            cursor="hand2"
        )

        row.pack(
            fill="x",
            padx=5
        )


        left = tk.Label(
            row,
            text=text,
            fg=TEXT,
            bg=BG,
            font=(
                "Segoe UI",
                10
            ),
            anchor="w"
        )

        left.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(14, 4),
            pady=6
        )


        right = tk.Label(
            row,
            text=shortcut,
            fg=MUTED,
            bg=BG,
            font=(
                "Segoe UI",
                9
            )
        )

        right.pack(
            side="right",
            padx=(4, 10)
        )


        def click(_=None):
            self.close_menu()

            command()


        for widget in (
            row,
            left,
            right
        ):
            widget.bind(
                "<Button-1>",
                click
            )


    # ========================================================
    # EMERGENCY RESTORE
    # ========================================================

    def emergency_restore(self):
        self.root.event_generate(
            "<<EmergencyRestore>>"
        )
import customtkinter as ctk
import webbrowser
import os
from resources import resource_path
from ui_category import CategoryPage

CATEGORY_COLORS = [
    "#1B3A5C", "#2D6A4F", "#6B2737",
    "#4A4A8A", "#7B4F00", "#1A5276",
    "#5B2333", "#145A32"
]

OVERLAY_BG   = "#1a2a3a"
GITHUB_URL   = "https://github.com/Shiruuukawa"
DEVELOPER    = "Developed by Shirukawa"
PFP_SIZE     = 100
GRID_COLS    = 5
BTN_W        = 185
BTN_H        = 130


class Dashboard(ctk.CTkFrame):
    def __init__(self, master, db, password, save_fn, on_logout):
        super().__init__(master, fg_color="transparent")
        self.master     = master
        self.db         = db
        self.password   = password
        self.save_fn    = save_fn
        self.on_logout  = on_logout
        self._overlay   = None
        self._pfp_image = None
        self.show_home()

    def _overlay_active(self) -> bool:
        return self._overlay is not None and self._overlay.winfo_exists()

    def _make_overlay(self, width: int, height: int,
                      border_color: str = "#2563AB",
                      bg_color: str = OVERLAY_BG):
        if self._overlay_active():
            return None
        ov = ctk.CTkFrame(
            self, width=width, height=height,
            fg_color=bg_color, corner_radius=16,
            border_width=2, border_color=border_color
        )
        ov.place(relx=0.5, rely=0.5, anchor="center")
        ov.pack_propagate(False)
        self._overlay = ov
        return ov

    def close_overlay(self) -> None:
        if self._overlay and self._overlay.winfo_exists():
            self._overlay.destroy()
        self._overlay = None

    def show_home(self) -> None:
        self._clear()

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(18, 0))

        brand = ctk.CTkFrame(top, fg_color="transparent")
        brand.pack(side="left")
        ctk.CTkLabel(
            brand, text="🔐 The Secret",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#4A90D9"
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand, text=f"Hello, {self.db.get('username', 'User')}!",
            font=ctk.CTkFont(size=16), text_color="gray"
        ).pack(anchor="w")

        ctk.CTkButton(
            top, text="Logout",
            width=130, height=42,
            fg_color="#8B0000", hover_color="#A00000",
            border_width=2, border_color="#FF4444",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.on_logout
        ).pack(side="right")

        self.grid_frame = ctk.CTkScrollableFrame(self)
        self.grid_frame.pack(fill="both", expand=True, padx=25, pady=12)
        self._render_grid()

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=20, pady=(4, 12))

        ctk.CTkButton(
            bottom, text="i",
            width=28, height=28,
            fg_color="#4A90D9", hover_color="#2563AB",
            text_color="#FFFFFF",
            border_width=2, border_color="#2563AB",
            corner_radius=4,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._toggle_info
        ).pack(side="left")

    def _render_grid(self) -> None:
        for w in self.grid_frame.winfo_children():
            w.destroy()

        categories = self.db.get("categories", {})
        items      = list(categories.keys()) + ["__add__"]
        row_frame  = None

        for idx, name in enumerate(items):
            if idx % GRID_COLS == 0:
                row_frame = ctk.CTkFrame(self.grid_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=6)

            if name == "__add__":
                btn = ctk.CTkButton(
                    row_frame, text="＋\nNew Category",
                    width=BTN_W, height=BTN_H,
                    fg_color="#1a2a3a", hover_color="#1B4F8A",
                    font=ctk.CTkFont(size=20),
                    command=self._show_add_overlay
                )
            else:
                cat   = categories[name]
                color   = cat.get("color", "#1B3A5C") if isinstance(cat, dict) else "#1B3A5C"
                entries = cat.get("entries", [])      if isinstance(cat, dict) else cat
                btn = ctk.CTkButton(
                    row_frame,
                    text=f"\n{name}\n({len(entries)} account/s)",
                    width=BTN_W, height=BTN_H,
                    fg_color=color, hover_color="#2563AB",
                    font=ctk.CTkFont(size=14),
                    command=lambda n=name: self._open_category(n)
                )
            btn.pack(side="left", padx=6)

    def _toggle_info(self) -> None:
        if self._overlay_active():
            self.close_overlay()
        else:
            self._show_info_overlay()

    def _show_info_overlay(self) -> None:
        if self._overlay_active():
            return

        ov = ctk.CTkFrame(
            self, width=280, height=240,
            fg_color="#0d1b2a", corner_radius=18,
            border_width=2, border_color="#4A90D9"
        )
        ov.place(x=20, rely=1.0, anchor="sw", y=-58)
        ov.pack_propagate(False)
        self._overlay = ov

        pfp_path  = resource_path("pfp.png")
        pfp_shown = False

        if os.path.exists(pfp_path):
            try:
                from PIL import Image, ImageDraw
                img  = Image.open(pfp_path).convert("RGBA")
                side = min(img.width, img.height)
                img  = img.crop((
                    (img.width  - side) // 2,
                    (img.height - side) // 2,
                    (img.width  + side) // 2,
                    (img.height + side) // 2
                ))
                img    = img.resize((PFP_SIZE, PFP_SIZE), Image.LANCZOS)
                mask   = Image.new("L", (PFP_SIZE, PFP_SIZE), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, PFP_SIZE, PFP_SIZE), fill=255)
                result = Image.new("RGBA", (PFP_SIZE, PFP_SIZE), (0, 0, 0, 0))
                result.paste(img, mask=mask)
                self._pfp_image = ctk.CTkImage(light_image=result, size=(PFP_SIZE, PFP_SIZE))
                ctk.CTkLabel(ov, image=self._pfp_image, text="").pack(pady=(18, 4))
                pfp_shown = True
            except Exception:
                pass

        if not pfp_shown:
            ctk.CTkLabel(
                ov, text="S",
                width=PFP_SIZE, height=PFP_SIZE,
                fg_color="#1B4F8A",
                corner_radius=PFP_SIZE // 2,
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color="#FFFFFF"
            ).pack(pady=(18, 4))

        ctk.CTkLabel(
            ov, text=DEVELOPER,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=(4, 0))

        lnk = ctk.CTkLabel(
            ov, text="github.com/Shiruuukawa",
            font=ctk.CTkFont(size=12, underline=True),
            text_color="#4A90D9", cursor="hand2"
        )
        lnk.pack(pady=(2, 14))
        lnk.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

    def _show_add_overlay(self) -> None:
        ov = self._make_overlay(460, 390, border_color="#2563AB", bg_color=OVERLAY_BG)
        if ov is None:
            return

        ctk.CTkLabel(
            ov, text="New Category",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        ).pack(pady=(26, 8))

        self._new_cat_name = ctk.CTkEntry(
            ov, placeholder_text="Category Name",
            width=380, height=50,
            font=ctk.CTkFont(size=16), border_width=2
        )
        self._new_cat_name.pack(pady=6)

        ctk.CTkLabel(
            ov, text="Select a category color:",
            font=ctk.CTkFont(size=13), text_color="#FFFFFF", anchor="w"
        ).pack(anchor="w", padx=42, pady=(8, 2))

        color_row = ctk.CTkFrame(ov, fg_color="transparent")
        color_row.pack(pady=4)

        self._chosen_color  = ctk.StringVar(value=CATEGORY_COLORS[0])
        self._color_btns    = {}

        for color in CATEGORY_COLORS:
            b = ctk.CTkButton(
                color_row, text="", width=34, height=34,
                fg_color=color, hover_color=color,
                border_width=3,
                border_color="#FFFFFF" if color == CATEGORY_COLORS[0] else color,
                corner_radius=17,
                command=lambda c=color: self._pick_color(c)
            )
            b.pack(side="left", padx=4)
            self._color_btns[color] = b

        btn_row = ctk.CTkFrame(ov, fg_color="transparent")
        btn_row.pack(pady=18)

        ctk.CTkButton(
            btn_row, text="Create", width=160, height=46,
            fg_color="#1B4F8A", hover_color="#2563AB",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._confirm_add_category
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="Cancel", width=160, height=46,
            fg_color="#333333", hover_color="#444444",
            font=ctk.CTkFont(size=15),
            command=self.close_overlay
        ).pack(side="left", padx=8)

    def _pick_color(self, color: str) -> None:
        self._chosen_color.set(color)
        for c, b in self._color_btns.items():
            b.configure(border_color="#FFFFFF" if c == color else c)

    def _confirm_add_category(self) -> None:
        name = self._new_cat_name.get().strip()
        if not name:
            return
        if name not in self.db["categories"]:
            self.db["categories"][name] = {
                "entries": [],
                "color":   self._chosen_color.get()
            }
            self.save_fn(self.db)
        self.close_overlay()
        self._render_grid()

    def _show_remove_category_overlay(self, name: str) -> None:
        ov = self._make_overlay(520, 330, border_color="#8B0000", bg_color="#FFFFFF")
        if ov is None:
            return

        ctk.CTkLabel(
            ov, text="⚠  Remove Category",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#CC0000"
        ).pack(pady=(26, 6))

        ctk.CTkLabel(
            ov, text=f'Do you want to remove "{name}"?',
            font=ctk.CTkFont(size=14), text_color="#111111"
        ).pack()

        ctk.CTkLabel(
            ov,
            text="Removing this category will permanently delete all accounts inside.\n"
                 "This cannot be undone. Proceed with caution.",
            font=ctk.CTkFont(size=12), text_color="#555555", wraplength=460
        ).pack(pady=8)

        ctk.CTkLabel(
            ov, text=f'Type  delete {name}  to confirm:',
            font=ctk.CTkFont(size=13, weight="bold"), text_color="#CC0000"
        ).pack(pady=(4, 2))

        self._delete_confirm_entry = ctk.CTkEntry(
            ov, placeholder_text=f'delete {name}',
            width=400, height=46,
            font=ctk.CTkFont(size=14), border_width=2,
            border_color="#CC0000"
        )
        self._delete_confirm_entry.pack(pady=4)

        self._delete_confirm_err = ctk.CTkLabel(
            ov, text="", text_color="red", font=ctk.CTkFont(size=12)
        )
        self._delete_confirm_err.pack()

        btn_row = ctk.CTkFrame(ov, fg_color="transparent")
        btn_row.pack(pady=10)

        ctk.CTkButton(
            btn_row, text="Yes, Delete", width=155, height=44,
            fg_color="#8B0000", hover_color="#A00000",
            font=ctk.CTkFont(size=15),
            command=lambda: self._execute_delete_category(name)
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="Cancel", width=155, height=44,
            fg_color="#555555", hover_color="#666666",
            font=ctk.CTkFont(size=15),
            command=self.close_overlay
        ).pack(side="left", padx=8)

    def _execute_delete_category(self, name: str) -> None:
        typed    = self._delete_confirm_entry.get().strip()
        expected = f"delete {name}"
        if typed != expected:
            self._delete_confirm_err.configure(text=f"Please type exactly:  {expected}")
            return
        del self.db["categories"][name]
        self.save_fn(self.db)
        self.close_overlay()
        self.show_home()

    def _show_remove_account_overlay(self, account_name: str, on_confirm) -> None:
        ov = self._make_overlay(460, 230, border_color="#8B0000", bg_color="#FFFFFF")
        if ov is None:
            return

        ctk.CTkLabel(
            ov, text="Remove Account",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#CC0000"
        ).pack(pady=(26, 6))

        ctk.CTkLabel(
            ov, text=f'Remove "{account_name}" from this category?',
            font=ctk.CTkFont(size=14), text_color="#111111"
        ).pack()

        ctk.CTkLabel(
            ov, text="This action is permanent and cannot be undone.",
            font=ctk.CTkFont(size=12), text_color="#555555"
        ).pack(pady=6)

        btn_row = ctk.CTkFrame(ov, fg_color="transparent")
        btn_row.pack(pady=12)

        ctk.CTkButton(
            btn_row, text="Yes, Remove", width=155, height=44,
            fg_color="#8B0000", hover_color="#A00000",
            font=ctk.CTkFont(size=15),
            command=lambda: [on_confirm(), self.close_overlay()]
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="Cancel", width=155, height=44,
            fg_color="#555555", hover_color="#666666",
            font=ctk.CTkFont(size=15),
            command=self.close_overlay
        ).pack(side="left", padx=8)

    def _open_category(self, name: str) -> None:
        self._clear()
        cat = self.db["categories"][name]
        if isinstance(cat, list):
            cat = {"entries": cat, "color": "#1B3A5C"}
            self.db["categories"][name] = cat

        def on_save(entries):
            self.db["categories"][name]["entries"] = entries
            self.save_fn(self.db)

        CategoryPage(
            self, name, cat["entries"],
            on_save=on_save,
            on_back=self.show_home,
            on_remove_category_request=lambda: self._show_remove_category_overlay(name),
            show_confirm_overlay=self._show_remove_account_overlay
        ).pack(fill="both", expand=True)

    def _clear(self) -> None:
        self.close_overlay()
        for w in self.winfo_children():
            w.destroy()

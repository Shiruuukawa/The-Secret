import customtkinter as ctk
import os
import sys
from resources import resource_path

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

APP_TITLE   = "The Secret"
APP_VERSION = "v1.0.4"
WIN_W       = 1280
WIN_H       = 720


class TheSecretApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} {APP_VERSION}")
        self.resizable(False, False)
        self._center_window(WIN_W, WIN_H)
        self._load_icon()
        self.current_password = None
        self.vault_data       = None
        self.show_login()

    def _center_window(self, w: int, h: int) -> None:
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _load_icon(self) -> None:
        try:
            ico = resource_path("icon.ico")
            png = resource_path("icon.png")
            if os.path.exists(ico):
                self.iconbitmap(ico)
            elif os.path.exists(png):
                from PIL import Image, ImageTk
                self.wm_iconphoto(True, ImageTk.PhotoImage(Image.open(png)))
        except Exception:
            pass

    def _clear_window(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self.update()

    def show_login(self) -> None:
        self._clear_window()
        from ui_login import LoginWindow
        LoginWindow(self, on_success=self._on_login_success).pack(fill="both", expand=True)
        self.update()

    def _on_login_success(self, password: str, data: dict) -> None:
        self.current_password = password
        self.vault_data       = data
        self._show_dashboard()

    def _show_dashboard(self) -> None:
        self._clear_window()
        from ui_dashboard import Dashboard
        Dashboard(
            self,
            db=self.vault_data,
            password=self.current_password,
            save_fn=self._save_vault,
            on_logout=self._on_logout
        ).pack(fill="both", expand=True)
        self.update()

    def _on_logout(self) -> None:
        self.current_password = None
        self.vault_data       = None
        self.show_login()

    def _save_vault(self, data: dict) -> None:
        from database import save_vault
        self.vault_data = data
        save_vault(self.current_password, data)


if __name__ == "__main__":
    TheSecretApp().mainloop()

import customtkinter as ctk
from auth import hash_password, verify_password
from database import load_vault, save_vault, vault_exists

ENTRY_W = 420
ENTRY_H = 54
BORDER  = 2


class LoginWindow(ctk.CTkFrame):
    def __init__(self, master, on_success):
        super().__init__(master, fg_color="transparent")
        self.master           = master
        self.on_success       = on_success
        self.is_first_run     = not vault_exists()
        self._pending_username = ""
        self._pending_password = ""
        self._build()

    def _build(self):
        container = self._new_container()
        self._draw_logo(container)
        if self.is_first_run:
            self._build_setup_step1(container)
        else:
            self._build_login(container)

    def _new_container(self):
        c = ctk.CTkFrame(self, fg_color="transparent")
        c.place(relx=0.5, rely=0.5, anchor="center")
        return c

    def _draw_logo(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=(0, 6))
        ctk.CTkLabel(row, text="🔐", font=ctk.CTkFont(size=54)).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(
            row, text="The Secret",
            font=ctk.CTkFont(size=54, weight="bold"),
            text_color="#4A90D9"
        ).pack(side="left")
        ctk.CTkLabel(
            parent, text="Your private password vault",
            font=ctk.CTkFont(size=16), text_color="gray"
        ).pack(pady=(0, 28))

    def _text_field(self, parent, placeholder):
        field = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            width=ENTRY_W, height=ENTRY_H,
            font=ctk.CTkFont(size=16), border_width=BORDER
        )
        field.pack(pady=6)
        return field

    def _password_field(self, parent, placeholder):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(pady=6)
        field = ctk.CTkEntry(
            row, placeholder_text=placeholder,
            width=ENTRY_W - 60, height=ENTRY_H,
            font=ctk.CTkFont(size=16), border_width=BORDER, show="•"
        )
        field.pack(side="left")
        visible = [False]

        def toggle_visibility():
            visible[0] = not visible[0]
            field.configure(show="" if visible[0] else "•")
            eye_btn.configure(text="🙈" if visible[0] else "👁")

        eye_btn = ctk.CTkButton(
            row, text="👁", width=52, height=ENTRY_H,
            fg_color="#1B3A5C", hover_color="#2563AB",
            font=ctk.CTkFont(size=18), command=toggle_visibility
        )
        eye_btn.pack(side="left", padx=(4, 0))
        return field

    def _error_label(self, parent):
        lbl = ctk.CTkLabel(parent, text="", text_color="red", font=ctk.CTkFont(size=13))
        lbl.pack(pady=4)
        return lbl

    def _reload(self, build_fn):
        for w in self.winfo_children():
            w.destroy()
        container = self._new_container()
        self._draw_logo(container)
        build_fn(container)

    def _build_setup_step1(self, container):
        ctk.CTkLabel(
            container, text="Create Your Vault",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(0, 14))

        self._f_username  = self._text_field(container, "Enter username")
        self._f_password  = self._password_field(container, "Enter password")
        self._f_pw_confirm = self._password_field(container, "Confirm password")
        self._err_step1   = self._error_label(container)

        ctk.CTkButton(
            container, text="Next",
            fg_color="#1B4F8A", hover_color="#2563AB",
            width=ENTRY_W, height=ENTRY_H,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self._advance_to_step2
        ).pack(pady=6)

    def _advance_to_step2(self):
        username = self._f_username.get().strip()
        password = self._f_password.get()
        confirm  = self._f_pw_confirm.get()

        if not username:
            self._err_step1.configure(text="Username is required.")
            return
        if not password:
            self._err_step1.configure(text="Password is required.")
            return
        if password != confirm:
            self._err_step1.configure(text="Passwords do not match.")
            return

        self._pending_username = username
        self._pending_password = password
        self._reload(self._build_setup_step2)

    def _build_setup_step2(self, container):
        ctk.CTkLabel(
            container, text="Set a Backup Password",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(0, 6))
        ctk.CTkLabel(
            container,
            text="Used to recover your vault if you forget your main password.",
            font=ctk.CTkFont(size=13), text_color="gray", wraplength=ENTRY_W
        ).pack(pady=(0, 18))

        self._f_backup         = self._password_field(container, "Enter backup password")
        self._f_backup_confirm = self._password_field(container, "Confirm backup password")
        self._err_step2        = self._error_label(container)

        nav = ctk.CTkFrame(container, fg_color="transparent")
        nav.pack(pady=6)

        ctk.CTkButton(
            nav, text="← Back",
            fg_color="transparent", border_width=BORDER,
            text_color="#4A90D9", hover_color="#1a2a3a",
            width=180, height=ENTRY_H, font=ctk.CTkFont(size=16),
            command=lambda: self._reload(
                lambda c: (self._build_setup_step1(c),
                           self._f_username.insert(0, self._pending_username))
            )
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            nav, text="Create Vault",
            fg_color="#1B4F8A", hover_color="#2563AB",
            width=230, height=ENTRY_H,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._finish_setup
        ).pack(side="left")

    def _finish_setup(self):
        backup  = self._f_backup.get()
        confirm = self._f_backup_confirm.get()

        if not backup:
            self._err_step2.configure(text="Backup password is required.")
            return
        if backup != confirm:
            self._err_step2.configure(text="Backup passwords do not match.")
            return

        data = {
            "username":        self._pending_username,
            "main_password":   hash_password(self._pending_password),
            "backup_password": hash_password(backup),
            "categories":      {}
        }
        save_vault(self._pending_password, data)
        self.on_success(self._pending_password, data)

    def _build_login(self, container):
        self._f_login_pw  = self._password_field(container, "Enter password")
        self._f_login_pw.bind("<Return>", lambda e: self._attempt_login())
        self._err_login   = self._error_label(container)

        ctk.CTkButton(
            container, text="Unlock",
            fg_color="#1B4F8A", hover_color="#2563AB",
            width=ENTRY_W, height=ENTRY_H,
            font=ctk.CTkFont(size=20, weight="bold"),
            command=self._attempt_login
        ).pack(pady=4)

        ctk.CTkButton(
            container, text="Forgot Password?",
            fg_color="transparent", text_color="#4A90D9",
            hover_color="#1a2a3a", font=ctk.CTkFont(size=13),
            command=self._show_reset
        ).pack(pady=6)

    def _attempt_login(self):
        pw   = self._f_login_pw.get()
        data = load_vault(pw)
        if data is None:
            self._err_login.configure(text="Wrong password or corrupted vault.")
            return
        if not verify_password(pw, data.get("main_password", "")):
            self._err_login.configure(text="Incorrect password.")
            return
        self.on_success(pw, data)

    def _show_reset(self):
        self._reload(self._build_reset_form)

    def _build_reset_form(self, container):
        ctk.CTkLabel(
            container, text="Reset Password",
            font=ctk.CTkFont(size=26, weight="bold")
        ).pack(pady=(0, 6))
        ctk.CTkLabel(
            container, text="Enter your backup password to set a new one.",
            font=ctk.CTkFont(size=14), text_color="gray"
        ).pack(pady=(0, 16))

        self._f_reset_backup  = self._password_field(container, "Enter backup password")
        self._f_reset_new     = self._password_field(container, "Enter new password")
        self._f_reset_confirm = self._password_field(container, "Confirm new password")
        self._err_reset       = self._error_label(container)

        ctk.CTkButton(
            container, text="Reset Password",
            fg_color="#1B4F8A", hover_color="#2563AB",
            width=ENTRY_W, height=ENTRY_H,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self._perform_reset
        ).pack(pady=4)

        ctk.CTkButton(
            container, text="← Back to Login",
            fg_color="transparent", text_color="#4A90D9",
            hover_color="#1a2a3a", font=ctk.CTkFont(size=13),
            command=self._back_to_login
        ).pack(pady=6)

    def _perform_reset(self):
        backup   = self._f_reset_backup.get()
        new_pw   = self._f_reset_new.get()
        confirm  = self._f_reset_confirm.get()

        if new_pw != confirm:
            self._err_reset.configure(text="New passwords don't match.")
            return
        data = load_vault(backup)
        if data is None:
            self._err_reset.configure(text="Could not decrypt — wrong backup password.")
            return
        if not verify_password(backup, data.get("backup_password", "")):
            self._err_reset.configure(text="Backup password is incorrect.")
            return

        data["main_password"] = hash_password(new_pw)
        save_vault(new_pw, data)
        self._err_reset.configure(text_color="green", text="Password reset! Redirecting…")
        self.after(1500, self._back_to_login)

    def _back_to_login(self):
        self._reload(self._build_login)

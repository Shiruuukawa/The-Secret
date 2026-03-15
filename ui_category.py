import customtkinter as ctk

ENTRY_H = 50
BORDER  = 2


class CategoryPage(ctk.CTkFrame):
    def __init__(self, master, category_name, entries, on_save,
                 on_back, on_remove_category_request, show_confirm_overlay):
        super().__init__(master, fg_color="transparent")
        self.category_name        = category_name
        self.entries              = list(entries)
        self.on_save              = on_save
        self.on_back              = on_back
        self.on_remove_request    = on_remove_category_request
        self.show_confirm_overlay = show_confirm_overlay
        self._pw_visible          = {}
        self._build_ui()

    def _build_ui(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=25, pady=(15, 5))

        ctk.CTkLabel(
            top, text=f"📁  {self.category_name}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#4A90D9"
        ).pack(side="left")

        ctk.CTkButton(
            top, text="← Back",
            width=110, height=40,
            fg_color="#1B4F8A", hover_color="#2563AB",
            border_width=2, border_color="#4A90D9",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.on_back
        ).pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            label_text="Accounts",
            label_font=ctk.CTkFont(size=15, weight="bold")
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=25, pady=8)
        self._render_entries()

        add_section = ctk.CTkFrame(self, corner_radius=10)
        add_section.pack(fill="x", padx=25, pady=(5, 6))

        ctk.CTkLabel(
            add_section, text="Add New Account",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(14, 6), padx=12)

        input_row = ctk.CTkFrame(add_section, fg_color="transparent")
        input_row.pack(fill="x", padx=12, pady=(0, 14))

        self._new_username = ctk.CTkEntry(
            input_row, placeholder_text="Username / Email",
            width=310, height=ENTRY_H,
            font=ctk.CTkFont(size=15), border_width=BORDER
        )
        self._new_username.pack(side="left", padx=(0, 8))

        self._new_password = ctk.CTkEntry(
            input_row, placeholder_text="Password",
            width=250, height=ENTRY_H,
            font=ctk.CTkFont(size=15), border_width=BORDER
        )
        self._new_password.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            input_row, text="+ Add Account",
            width=150, height=ENTRY_H,
            fg_color="#1B4F8A", hover_color="#2563AB",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._add_entry
        ).pack(side="left")

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=25, pady=(0, 14))

        ctk.CTkButton(
            bottom, text="Remove Category",
            width=175, height=40,
            fg_color="#8B0000", hover_color="#A00000",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.on_remove_request
        ).pack(side="right")

    def _render_entries(self) -> None:
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        if not self.entries:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No accounts yet. Add one below.",
                font=ctk.CTkFont(size=14), text_color="gray"
            ).pack(pady=24)
            return

        for idx, entry in enumerate(self.entries):
            row = ctk.CTkFrame(self.scroll_frame, corner_radius=10, height=70)
            row.pack(fill="x", pady=5, padx=5)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text="👤", font=ctk.CTkFont(size=22)).pack(side="left", padx=16)

            ctk.CTkLabel(
                row, text=entry["username"],
                font=ctk.CTkFont(size=15), width=200, anchor="w"
            ).pack(side="left", padx=(6, 2))

            ctk.CTkButton(
                row, text="Copy", width=55, height=32,
                fg_color="#2D6A4F", hover_color="#3A8A65",
                font=ctk.CTkFont(size=12),
                command=lambda u=entry["username"]: self._copy_to_clipboard(u)
            ).pack(side="left", padx=(0, 12))

            pw_display = ctk.StringVar(value="••••••••")
            ctk.CTkLabel(
                row, textvariable=pw_display,
                font=ctk.CTkFont(size=15), width=150, anchor="w"
            ).pack(side="left", padx=(6, 2))

            ctk.CTkButton(
                row, text="Copy", width=55, height=32,
                fg_color="#2D6A4F", hover_color="#3A8A65",
                font=ctk.CTkFont(size=12),
                command=lambda i=idx: self._copy_to_clipboard(self.entries[i]["password"])
            ).pack(side="left", padx=(0, 12))

            self._pw_visible[idx] = False

            def toggle_pw(i=idx, var=pw_display):
                self._pw_visible[i] = not self._pw_visible[i]
                var.set(self.entries[i]["password"] if self._pw_visible[i] else "••••••••")

            ctk.CTkButton(
                row, text="View", width=80, height=36,
                fg_color="#1B4F8A", hover_color="#2563AB",
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=toggle_pw
            ).pack(side="left", padx=(0, 6))

            ctk.CTkButton(
                row, text="Remove", width=80, height=36,
                fg_color="#8B0000", hover_color="#A00000",
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda i=idx: self._request_remove(i)
            ).pack(side="left", padx=(0, 6))

    def _copy_to_clipboard(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self._show_copy_toast()

    def _show_copy_toast(self) -> None:
        root   = self.winfo_toplevel()
        toast  = ctk.CTkLabel(
            root, text="✔  Copied to clipboard!",
            fg_color="#2D6A4F", text_color="#FFFFFF",
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            padx=16, pady=8
        )
        toast.place(relx=0.5, rely=0.02, anchor="n")
        root.after(1500, toast.destroy)

    def _request_remove(self, idx: int) -> None:
        def confirm():
            self.entries.pop(idx)
            self.on_save(self.entries)
            self._render_entries()

        self.show_confirm_overlay(self.entries[idx]["username"], confirm)

    def _add_entry(self) -> None:
        username = self._new_username.get().strip()
        password = self._new_password.get().strip()
        if not username or not password:
            return
        self.entries.append({"username": username, "password": password})
        self._new_username.delete(0, "end")
        self._new_password.delete(0, "end")
        self.on_save(self.entries)
        self._render_entries()

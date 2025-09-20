"""Tkinter GUI skeleton for the password manager.

Two screens:
- LoginFrame: asks for master password, initializes services
- VaultFrame: lists passwords and allows add/delete

This is a minimal, synchronous UI intended as a starting point. No theming yet.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional

from . import services


class LoginFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, on_login):
        super().__init__(master)
        self.on_login = on_login

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Master password:").grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=0, column=1, padx=8, pady=8, sticky=tk.EW)
        self.password_entry.bind("<Return>", lambda e: self.login())

        self.login_btn = ttk.Button(self, text="Login", command=self.login)
        self.login_btn.grid(row=1, column=0, columnspan=2, padx=8, pady=8, sticky=tk.EW)

    def login(self):
        pw = self.password_var.get().strip()
        if not pw:
            messagebox.showwarning("Missing", "Please enter the master password")
            return
        try:
            key = services.initialize(pw)
        except Exception as ex:
            messagebox.showerror("Error", f"Initialization failed: {ex}")
            return
        self.on_login(key)


class VaultFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, key: bytes):
        super().__init__(master)
        self.key = key

        # Toolbar
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="Add", command=self.add_item).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(bar, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=4, pady=4)

        # Treeview
        columns = ("id", "site", "username", "password")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse", height=12)
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            items = services.list_passwords(self.key)
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to list passwords: {ex}")
            return
        for it in items:
            self.tree.insert("", tk.END, values=(it["id"], it["site"], it["username"], it["password"]))

    def add_item(self):
        site = simpledialog.askstring("Site", "Enter site")
        if not site:
            return
        username = simpledialog.askstring("Username", "Enter username")
        if not username:
            return
        password = simpledialog.askstring("Password", "Enter password", show="*")
        if password is None:
            return
        try:
            services.add_password(self.key, site, username, password)
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to add: {ex}")
            return
        self.refresh()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        entry_id = int(values[0])
        if not messagebox.askyesno("Confirm", "Delete selected entry?"):
            return
        ok = services.delete_password(entry_id)
        if not ok:
            messagebox.showwarning("Not found", "Entry not deleted")
        self.refresh()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AmparaPass - Password Manager")
        self.geometry("720x480")

        self.current_frame: Optional[ttk.Frame] = None
        self.show_login()

    def set_frame(self, frame: ttk.Frame):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def show_login(self):
        self.set_frame(LoginFrame(self, on_login=self.show_vault))

    def show_vault(self, key: bytes):
        self.set_frame(VaultFrame(self, key))

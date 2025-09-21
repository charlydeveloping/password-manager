from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from .. import services


class VaultFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, user_id: int, key: bytes):
        super().__init__(master)
        self.user_id = user_id
        self.key = key

        # Toolbar
        bar = ttk.Frame(self)
        bar.pack(fill=tk.X)
        # User info
        info = services.get_user_profile(self.user_id) or {"full_name": "", "email": "", "username": ""}
        self.user_label = ttk.Label(bar, text=f"User: {info['full_name']} <{info['email']}>".strip())
        self.user_label.pack(side=tk.LEFT, padx=6)

        ttk.Button(bar, text="Add", command=self.add_item).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(bar, text="Refresh", command=self.refresh).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(bar, text="Delete", command=self.delete_selected).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(bar, text="Change Password", command=self.change_password).pack(side=tk.RIGHT, padx=4, pady=4)
        ttk.Button(bar, text="Logout", command=self.logout).pack(side=tk.RIGHT, padx=4, pady=4)

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
            items = services.list_passwords(self.user_id, self.key)
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
            services.add_password(self.user_id, self.key, site, username, password)
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
        ok = services.delete_password(self.user_id, entry_id)
        if not ok:
            messagebox.showwarning("Not found", "Entry not deleted")
        self.refresh()

    def logout(self):
        if not messagebox.askyesno("Confirm", "Return to login?"):
            return
        try:
            # Best-effort: clear key reference
            self.key = b""
        except Exception:
            pass
        # Delegate navigation to the App controller
        if hasattr(self.master, "show_login"):
            self.master.show_login()

    def change_password(self):
        old_pw = simpledialog.askstring("Old Password", "Enter old password", show='*')
        if old_pw is None:
            return
        new_pw = simpledialog.askstring("New Password", "Enter new password", show='*')
        if new_pw is None:
            return
        new_pw2 = simpledialog.askstring("Confirm", "Confirm new password", show='*')
        if new_pw2 is None:
            return
        if new_pw != new_pw2:
            messagebox.showwarning("Mismatch", "Passwords do not match")
            return
        try:
            services.change_master_password(self.user_id, old_pw, new_pw)
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to change password: {ex}")
            return
        messagebox.showinfo("Success", "Master password updated")

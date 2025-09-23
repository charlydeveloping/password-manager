from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from .. import services


class LoginFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, on_login):
        super().__init__(master)
        self.on_login = on_login

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Usuario:").grid(row=0, column=0, padx=8, pady=8, sticky=tk.W)
        self.username_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.username_var).grid(row=0, column=1, padx=8, pady=8, sticky=tk.EW)

        ttk.Label(self, text="Contraseña maestra:").grid(row=1, column=0, padx=8, pady=8, sticky=tk.W)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=1, column=1, padx=8, pady=8, sticky=tk.EW)
        self.password_entry.bind("<Return>", lambda e: self.login())

        btns = ttk.Frame(self)
        btns.grid(row=2, column=0, columnspan=2, padx=8, pady=8, sticky=tk.EW)
        self.login_btn = ttk.Button(btns, text="Iniciar Sesión", command=self.login)
        self.login_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
        self.register_btn = ttk.Button(btns, text="Registrarse", command=self.register)
        self.register_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def login(self):
        user = self.username_var.get().strip()
        pw = self.password_var.get().strip()
        if not user or not pw:
            messagebox.showwarning("Campos requeridos", "Por favor ingrese usuario y contraseña")
            return
        try:
            user_id, key = services.login(user, pw)
        except Exception as ex:
            messagebox.showerror("Error", f"Error de inicio de sesión: {ex}")
            return
        # callback expects (user_id, key)
        try:
            self.on_login(user_id, key)
        except TypeError:
            # backward compatibility if callback expects a tuple
            self.on_login((user_id, key))

    def register(self):
        if hasattr(self.master, "show_register"):
            self.master.show_register()

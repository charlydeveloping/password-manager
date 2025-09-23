from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from .. import services


class RegisterFrame(ttk.Frame):
    def __init__(self, master: tk.Tk, on_registered):
        super().__init__(master)
        self.on_registered = on_registered

        self.columnconfigure(1, weight=1)

        ttk.Label(self, text="Usuario:").grid(row=0, column=0, padx=8, pady=4, sticky=tk.W)
        self.username_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.username_var).grid(row=0, column=1, padx=8, pady=4, sticky=tk.EW)

        ttk.Label(self, text="Nombre completo:").grid(row=1, column=0, padx=8, pady=4, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var).grid(row=1, column=1, padx=8, pady=4, sticky=tk.EW)

        ttk.Label(self, text="Correo electrónico:").grid(row=2, column=0, padx=8, pady=4, sticky=tk.W)
        self.email_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.email_var).grid(row=2, column=1, padx=8, pady=4, sticky=tk.EW)

        ttk.Label(self, text="Contraseña maestra:").grid(row=3, column=0, padx=8, pady=4, sticky=tk.W)
        self.pw_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.pw_var, show='*').grid(row=3, column=1, padx=8, pady=4, sticky=tk.EW)

        ttk.Label(self, text="Confirmar contraseña:").grid(row=4, column=0, padx=8, pady=4, sticky=tk.W)
        self.pw2_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.pw2_var, show='*').grid(row=4, column=1, padx=8, pady=4, sticky=tk.EW)

        btns = ttk.Frame(self)
        btns.grid(row=5, column=0, columnspan=2, padx=8, pady=8, sticky=tk.EW)
        ttk.Button(btns, text="Crear cuenta", command=self.register).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,4))
        ttk.Button(btns, text="Volver", command=self.back).pack(side=tk.LEFT, expand=True, fill=tk.X)

    def back(self):
        if hasattr(self.master, 'show_login'):
            self.master.show_login()

    def register(self):
        username = self.username_var.get().strip()
        name = self.name_var.get().strip()
        email = self.email_var.get().strip()
        pw = self.pw_var.get().strip()
        pw2 = self.pw2_var.get().strip()
        if not username:
            messagebox.showwarning('Campo requerido', 'El nombre de usuario es requerido')
            return
        if not pw or not pw2:
            messagebox.showwarning('Campo requerido', 'La contraseña es requerida')
            return
        if pw != pw2:
            messagebox.showwarning('Error de confirmación', 'Las contraseñas no coinciden')
            return
        try:
            user_id, key = services.register_user(username, name, email, pw)
        except Exception as ex:
            messagebox.showerror('Error', f'Error en el registro: {ex}')
            return
        try:
            self.on_registered(user_id, key)
        except TypeError:
            self.on_registered((user_id, key))

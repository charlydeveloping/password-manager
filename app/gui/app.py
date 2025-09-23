from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from .login import LoginFrame
from .vault import VaultFrame
from .register import RegisterFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Charly Password Manager")
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

    def show_vault(self, user_id: int, key: bytes):
        self.set_frame(VaultFrame(self, user_id, key))

    def show_register(self):
        self.set_frame(RegisterFrame(self, on_registered=self.show_vault))

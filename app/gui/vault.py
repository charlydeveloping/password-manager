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
        self.user_label = ttk.Label(bar, text=f"Usuario: {info['full_name']} <{info['email']}>".strip())
        self.user_label.pack(side=tk.LEFT, padx=6)

        ttk.Button(bar, text="Agregar", command=self.add_item).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(bar, text="Actualizar", command=self.refresh).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(bar, text="Eliminar", command=self.delete_selected).pack(side=tk.LEFT, padx=4, pady=4)
        self.btn_show_hide = ttk.Button(bar, text="Mostrar/Ocultar", command=self._toggle_password, state=tk.DISABLED)
        self.btn_show_hide.pack(side=tk.LEFT, padx=4, pady=4)
        self.btn_change_entry = ttk.Button(bar, text="Cambiar Contraseña", command=self._change_selected_password, state=tk.DISABLED)
        self.btn_change_entry.pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(bar, text="Cambiar Clave Maestra", command=self.change_password).pack(side=tk.RIGHT, padx=4, pady=4)
        ttk.Button(bar, text="Cerrar Sesión", command=self.logout).pack(side=tk.RIGHT, padx=4, pady=4)

        # Treeview
        columns = ("id", "site", "username", "password")
        column_headers = {"id": "ID", "site": "Sitio", "username": "Usuario", "password": "Contraseña"}
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse", height=12)
        for col in columns:
            self.tree.heading(col, text=column_headers[col])
            self.tree.column(col, stretch=True)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Helper hint
        hint = ttk.Label(self, text="Selecciona una fila y usa Mostrar/Ocultar o Cambiar contraseña. También puedes clic derecho para más opciones.")
        hint.pack(fill=tk.X, padx=6, pady=(2, 6))

        # Track entries whose password is shown (default is masked)
        self._shown_ids = set()
        self.tree.bind("<Button-3>", self._on_context_menu)
        # macOS ctrl+click context menu
        self.tree.bind("<Control-Button-1>", self._on_context_menu)
        # Update action buttons when selection changes
        self.tree.bind("<<TreeviewSelect>>", self._on_selection_changed)

        self.refresh()

    def refresh(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            items = services.list_passwords(self.user_id, self.key)
        except Exception as ex:
            messagebox.showerror("Error", f"Error al listar contraseñas: {ex}")
            return
        for it in items:
            pwd = it["password"]
            if pwd == "<unable to decrypt>":
                pwd_display = pwd
            elif it["id"] in self._shown_ids:
                pwd_display = pwd
            else:
                pwd_display = "•" * min(len(pwd), 12)
            self.tree.insert("", tk.END, values=(it["id"], it["site"], it["username"], pwd_display))

    def add_item(self):
        site = simpledialog.askstring("Sitio", "Ingrese el sitio web")
        if not site:
            return
        username = simpledialog.askstring("Usuario", "Ingrese el nombre de usuario")
        if not username:
            return
        password = simpledialog.askstring("Contraseña", "Ingrese la contraseña", show="*")
        if password is None:
            return
        try:
            services.add_password(self.user_id, self.key, site, username, password)
        except Exception as ex:
            messagebox.showerror("Error", f"Error al agregar: {ex}")
            return
        self.refresh()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0], "values")
        entry_id = int(values[0])
        if not messagebox.askyesno("Confirmar", "¿Eliminar la entrada seleccionada?"):
            return
        ok = services.delete_password(self.user_id, entry_id)
        if not ok:
            messagebox.showwarning("No encontrado", "Entrada no eliminada")
        self.refresh()

    def logout(self):
        if not messagebox.askyesno("Confirmar", "¿Volver al inicio de sesión?"):
            return
        try:
            # Best-effort: clear key reference
            self.key = b""
        except Exception:
            pass
        # Delegate navigation to the App controller
        if hasattr(self.master, "show_login"):
            self.master.show_login()

    # Context menu actions
    def _on_context_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Mostrar/Ocultar Contraseña", command=self._toggle_password)
        menu.add_command(label="Cambiar Contraseña", command=self._change_selected_password)
        menu.add_separator()
        menu.add_command(label="Eliminar", command=self.delete_selected)
        menu.tk_popup(event.x_root, event.y_root)

    def _get_selected_entry(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        return int(values[0]) if values else None

    def _on_selection_changed(self, _event=None):
        has_selection = bool(self.tree.selection())
        self.btn_show_hide.configure(state=(tk.NORMAL if has_selection else tk.DISABLED))
        self.btn_change_entry.configure(state=(tk.NORMAL if has_selection else tk.DISABLED))

    def _toggle_password(self):
        entry_id = self._get_selected_entry()
        if entry_id is None:
            return
        if entry_id in self._shown_ids:
            self._shown_ids.remove(entry_id)
        else:
            self._shown_ids.add(entry_id)
        self.refresh()

    def _change_selected_password(self):
        entry_id = self._get_selected_entry()
        if entry_id is None:
            return
        new_pw = simpledialog.askstring("Cambiar Contraseña", "Ingrese la nueva contraseña", show='*')
        if not new_pw:
            return
        try:
            services.update_password(self.user_id, self.key, entry_id, new_pw)
        except Exception as ex:
            messagebox.showerror("Error", f"Error al actualizar contraseña: {ex}")
            return
        self.refresh()

    def change_password(self):
        old_pw = simpledialog.askstring("Contraseña Anterior", "Ingrese la contraseña anterior", show='*')
        if old_pw is None:
            return
        new_pw = simpledialog.askstring("Nueva Contraseña", "Ingrese la nueva contraseña", show='*')
        if new_pw is None:
            return
        new_pw2 = simpledialog.askstring("Confirmar", "Confirme la nueva contraseña", show='*')
        if new_pw2 is None:
            return
        if new_pw != new_pw2:
            messagebox.showwarning("Error de confirmación", "Las contraseñas no coinciden")
            return
        try:
            services.change_master_password(self.user_id, old_pw, new_pw)
        except Exception as ex:
            messagebox.showerror("Error", f"Error al cambiar contraseña: {ex}")
            return
        messagebox.showinfo("Éxito", "Contraseña maestra actualizada")

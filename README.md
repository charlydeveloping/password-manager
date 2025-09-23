# PasswordManager - Password Manager (Tkinter)

Pequeño gestor de contraseñas con interfaz de escritorio usando Tkinter, cifrado con `cryptography` (Fernet) y almacenamiento en SQLite.

## Características
- Derivación de clave maestra con PBKDF2HMAC (SHA-256)
- Cifrado/descifrado con Fernet (AEAD)
- Persistencia local en SQLite (`~/.passwordmanager/passwords.db`); salt por usuario almacenado en la tabla `users`
- Interfaz simple con Tkinter: login y CRUD básico

## Requisitos
- Python 3.10+
- Paquete `cryptography`
- Tkinter: incluido en macOS/Windows; en Linux se puede requerir `python3-tk`.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Linux, si falta Tkinter:
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install -y python3-tk
```

## Uso

```bash
python main.py
```

- Primera vez: regístrate con `username`, nombre, email y contraseña maestra (se generará un salt por usuario en DB).
- Inicia sesión con `username` + contraseña maestra.

## Estructura

- `main.py`: punto de entrada.
- `app/gui.py`: UI con Tkinter (login y gestión de contraseñas: agregar, listar, eliminar).
- `app/crypto.py`: derivación de clave y cifrado/descifrado.
- `app/storage.py`: persistencia SQLite (tabla `vault`).
- `app/services.py`: lógica de negocio entre crypto y storage.
- `app/config.py`: rutas y constantes.
- `tests/`: pruebas unitarias básicas.


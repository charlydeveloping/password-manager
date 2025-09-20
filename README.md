# AmparaPass - Password Manager (Tkinter)

Pequeño gestor de contraseñas con interfaz de escritorio usando Tkinter, cifrado con `cryptography` (Fernet) y almacenamiento en SQLite.

## Características
- Derivación de clave maestra con PBKDF2HMAC (SHA-256)
- Cifrado/descifrado con Fernet (AEAD)
- Persistencia local en SQLite (`~/.amparapass/passwords.db`)
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

- La primera vez crea `~/.amparapass/`, la base de datos y un archivo de `salt`.
- Inicia sesión con una contraseña maestra (se derivará la clave y se usará para cifrar/descifrar).

## Estructura

- `main.py`: punto de entrada.
- `app/gui.py`: UI con Tkinter (login y gestión de contraseñas: agregar, listar, eliminar).
- `app/crypto.py`: derivación de clave y cifrado/descifrado.
- `app/storage.py`: persistencia SQLite (tabla `vault`).
- `app/services.py`: lógica de negocio entre crypto y storage.
- `app/config.py`: rutas y constantes.
- `tests/`: pruebas unitarias básicas.

## Notas de seguridad
- Este proyecto es educativo; revisa y fortalece antes de uso real.
- La rotación de `salt` romperá los datos existentes; no la cambies sin plan de migración.
- Considera ocultar la contraseña en el Treeview y copiar al portapapeles bajo demanda.

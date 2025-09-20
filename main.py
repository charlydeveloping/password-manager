"""Entry point for the Password Manager app.

This launches a simple Tkinter GUI. Run as:
    python -m main
or:
    python main.py
"""
from __future__ import annotations

import sys

try:
    from app.gui import App
except Exception as ex:
    print(f"Failed to import application: {ex}")
    sys.exit(1)


def main() -> int:
    app = App()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

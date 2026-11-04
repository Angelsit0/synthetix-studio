"""Colores ANSI para la consola, en un solo lugar.

Los colores se desactivan solos cuando la salida no es una terminal (redirigida a un
archivo, la prueba de humo, GitHub Actions) o cuando existe la variable de entorno
NO_COLOR (convención de https://no-color.org). Así la salida redirigida queda limpia.
"""
from __future__ import annotations

import os
import sys

RED = "91"
GREEN = "92"
YELLOW = "93"
BLUE = "94"
CYAN = "96"
WHITE = "97"
GRAY = "90"
PINK = "38;5;213"


def enabled() -> bool:
    """True si conviene usar colores. Se consulta en cada llamada (es barato)."""
    if "NO_COLOR" in os.environ:
        return False
    stream = sys.stdout
    return hasattr(stream, "isatty") and stream.isatty()


def paint(text: str, color: str) -> str:
    """Devuelve text coloreado, o tal cual si los colores están desactivados."""
    if not enabled():
        return text
    return f"\033[{color}m{text}\033[0m"

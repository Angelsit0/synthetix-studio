"""Log de errores y eventos en <paths.logs>/synthetix.log (ruta tomada de config.json).

Es thread-safe porque el hilo de la cola de IA también registra eventos.
"""
from __future__ import annotations

import os
import threading
from datetime import datetime


class Logger:
    def __init__(self) -> None:
        self._path = ""
        self._lock = threading.Lock()

    def init(self, directory: str) -> None:
        with self._lock:
            os.makedirs(directory, exist_ok=True)
            self._path = os.path.join(directory, "synthetix.log")

    @property
    def file_path(self) -> str:
        return self._path

    def info(self, message: str) -> None:
        self._write("INFO", message)

    def error(self, message: str) -> None:
        self._write("ERROR", message)

    def _write(self, level: str, message: str) -> None:
        with self._lock:
            if not self._path:
                return
            stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self._path, "a", encoding="utf-8") as out:
                out.write(f"[{stamp}] [{level}] {message}\n")

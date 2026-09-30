"""Lectura del archivo de configuración externo (config.json).

Las claves se consultan con puntos: config.get("api.base_url").
"""
from __future__ import annotations

import json
import os
from typing import Any


class ConfigError(Exception):
    pass


class Config:
    def __init__(self) -> None:
        self._data: dict = {}
        self._source = ""

    def load_from_file(self, path: str) -> None:
        """Carga el archivo. Si falla, lanza ConfigError y conserva la configuración anterior."""
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise ConfigError(f"no existe el archivo '{path}'") from None
        except json.JSONDecodeError as e:
            raise ConfigError(f"JSON inválido en la línea {e.lineno}: {e.msg}") from None
        if not isinstance(data, dict):
            raise ConfigError("el archivo debe contener un objeto JSON")
        self._data = data
        self._source = path

    @property
    def source_path(self) -> str:
        return self._source

    @property
    def is_loaded(self) -> bool:
        return bool(self._source)

    def get(self, key: str, fallback: Any = None) -> Any:
        node: Any = self._data
        for part in key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return fallback
        return node

    def get_int(self, key: str, fallback: int) -> int:
        try:
            return int(self.get(key, fallback))
        except (TypeError, ValueError):
            return fallback

    @property
    def backup_dir(self) -> str:
        return self.get("paths.backups", "./backups")

    @property
    def log_dir(self) -> str:
        return self.get("paths.logs", "./logs")

    @property
    def api_base_url(self) -> str:
        return self.get("api.base_url", "")

    @property
    def api_url(self) -> str:
        return self.api_base_url + self.get("api.endpoint", "")

    @property
    def api_model(self) -> str:
        return self.get("api.model", "")

    @property
    def api_timeout(self) -> int:
        return self.get_int("api.timeout_seconds", 30)

    @property
    def api_key(self) -> str:
        """La clave NUNCA va en config.json: se lee de la variable de entorno api.api_key_env."""
        return os.environ.get(self.get("api.api_key_env", "SYNTHETIX_API_KEY"), "")

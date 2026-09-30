"""Respaldos en la carpeta indicada por config.json (paths.backups).

Se usa con el comando save, al eliminar un archivo modificado y al salir.
"""
from __future__ import annotations

import os
from datetime import datetime

from synthetix.files.code_file import CodeFile


class BackupManager:
    @staticmethod
    def backup(file: CodeFile, directory: str) -> str:
        """Crea <directorio>/<nombre>_<fecha>.bak y devuelve la ruta creada."""
        os.makedirs(directory, exist_ok=True)
        safe_name = file.name
        for bad in ("/", "\\", ":"):
            safe_name = safe_name.replace(bad, "_")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(directory, f"{safe_name}_{stamp}.bak")
        with open(path, "w", encoding="utf-8") as out:
            out.write(file.content)
        return path

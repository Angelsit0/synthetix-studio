"""Aplicación principal. No debería hacer falta tocarla: cada módulo registra sus comandos."""
from __future__ import annotations

import sys

from synthetix.commands.ai_commands import AICommandModule
from synthetix.commands.analysis_commands import AnalysisCommandModule
from synthetix.commands.core_commands import CoreCommandModule
from synthetix.commands.file_commands import FileCommandModule
from synthetix.commands.validation_commands import ValidationCommandModule
from synthetix.config.config import ConfigError
from synthetix.core.app_context import AppContext
from synthetix.core.command_registry import CommandRegistry
from synthetix.core.console import Console
from synthetix.files.backup_manager import BackupManager


class Application:
    def run(self, argv: list) -> int:
        self._configure_output()
        ctx = AppContext()

        # El enunciado exige leer la configuración al iniciar.
        config_path = argv[1] if len(argv) > 1 else "config.json"
        try:
            ctx.config.load_from_file(config_path)
        except ConfigError as e:
            print(f"[error] No se pudo leer la configuración '{config_path}': {e}")
            print("Uso: python main.py [ruta/config.json]")
            return 1
        ctx.logger.init(ctx.config.log_dir)
        ctx.logger.info(f"Inicio de sesión con {config_path}")
        print(f"Configuración cargada: {config_path}")

        registry = CommandRegistry()
        for module in (CoreCommandModule, FileCommandModule, ValidationCommandModule,
                       AnalysisCommandModule, AICommandModule):
            module.register_into(registry)

        ctx.requests.start()
        Console(registry, ctx).run()
        ctx.requests.stop()
        self._backup_on_exit(ctx)
        ctx.logger.info("Fin de sesión")
        return 0

    @staticmethod
    def _backup_on_exit(ctx: AppContext) -> None:
        """Respaldo automático de lo que quedó sin guardar."""
        try:
            for file in ctx.files:
                if file.modified:
                    path = BackupManager.backup(file, ctx.config.backup_dir)
                    print(f"Respaldo automático: {path}")
        except Exception as e:  # noqa: BLE001
            ctx.logger.error(f"Respaldo al salir: {e}")

    @staticmethod
    def _configure_output() -> None:
        """Evita errores con tildes en la consola de Windows y habilita ANSI."""
        import os
        if os.name == "nt":
            os.system("")  # Habilita secuencias ANSI en la consola de Windows
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")

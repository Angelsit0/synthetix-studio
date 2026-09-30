"""Comandos generales. DUEÑO: Angel Torres (integración)"""
from __future__ import annotations

from synthetix.config.config import ConfigError
from synthetix.core.command import Command
from synthetix.core.command_registry import CommandRegistry


class HelpCommand(Command):
    name = "help"
    usage = "help"
    description = "Muestra los comandos disponibles"

    def __init__(self, registry: CommandRegistry) -> None:
        self._registry = registry

    def execute(self, args, ctx) -> None:
        print("Comandos disponibles:")
        for command in self._registry:
            print(f"  {command.usage:<56}{command.description}")


class ConfigCommand(Command):
    name = "config"
    usage = "config <ruta_archivo>"
    description = "Carga el archivo de configuración (rutas y endpoints)"
    min_args = 1

    def execute(self, args, ctx) -> None:
        try:
            ctx.config.load_from_file(args[1])
        except ConfigError as e:
            raise RuntimeError(f"No se pudo cargar '{args[1]}': {e}") from None
        ctx.logger.init(ctx.config.log_dir)
        ctx.logger.info(f"Configuración cargada desde {args[1]}")
        print(f"Configuración cargada desde {args[1]}")
        print(f"  Respaldos: {ctx.config.backup_dir}")
        print(f"  Logs:      {ctx.config.log_dir}")
        print(f"  API:       {ctx.config.api_url} (modelo {ctx.config.api_model})")
        estado = "encontrada" if ctx.config.api_key else "NO encontrada en la variable de entorno"
        print(f"  Clave API: {estado}")


class ExitCommand(Command):
    name = "exit"
    usage = "exit"
    description = "Sale (respalda automáticamente los archivos modificados)"

    def execute(self, args, ctx) -> None:
        ctx.running = False
        print("Cerrando Synthetix Studio...")


class CoreCommandModule:
    @staticmethod
    def register_into(registry: CommandRegistry) -> None:
        registry.add(HelpCommand(registry))
        registry.add(ConfigCommand())
        registry.add(ExitCommand())

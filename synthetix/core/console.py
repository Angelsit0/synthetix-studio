"""Invoker del patrón Command: lee líneas, busca el comando y lo ejecuta.

Los errores de cualquier comando se muestran y se registran en el log; la consola nunca se cae.
"""
from __future__ import annotations

from synthetix.core.app_context import AppContext
from synthetix.core.command_args import CommandArgs
from synthetix.core.command_registry import CommandRegistry
from synthetix.util import colors
from synthetix.util.colors import paint


class Console:
    def __init__(self, registry: CommandRegistry, ctx: AppContext) -> None:
        self._registry = registry
        self._ctx = ctx

    def run(self) -> None:
        self._print_banner()
        while self._ctx.running:
            try:
                line = input(self._prompt())
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print("\nUsa 'exit' para salir.")
                continue
            self.execute_line(line)

    def execute_line(self, line: str) -> None:
        args = CommandArgs.parse(line)
        if args.is_empty() or args.name.startswith("#"):
            return  # línea vacía o comentario (útil en scripts de prueba)

        command = self._registry.find(args.name)
        if command is None:
            print(f"Comando desconocido: '{args.name}'. Escribe 'help' para ver los comandos.")
            return
        if args.count() - 1 < command.min_args:
            print(f"Uso: {command.usage}")
            return
        try:
            command.execute(args, self._ctx)
        except Exception as e:  # noqa: BLE001 - la consola no debe caerse nunca
            print(f"{paint('[error]', colors.RED)} {e}")
            self._ctx.logger.error(f"{args.name}: {e}")

    def _prompt(self) -> str:
        active = self._ctx.files.active
        if active:
            return f"{paint('synthetix', colors.GREEN)}({paint(active.name, colors.CYAN)})> "
        return f"{paint('synthetix', colors.GREEN)}> "

    @staticmethod
    def _print_banner() -> None:
        """Encabezado de bienvenida (sin pausas: no retrasa scripts ni la prueba de humo)."""
        banner = ("  ╔══════════════════════════════╗\n"
                  "  ║   S Y N T H E T I X          ║\n"
                  "  ║   Studio · Mini IDE          ║\n"
                  "  ╚══════════════════════════════╝")
        print(paint(banner, colors.PINK))
        print(paint("  Escribe 'help' para ver los comandos.", colors.GRAY) + "\n")

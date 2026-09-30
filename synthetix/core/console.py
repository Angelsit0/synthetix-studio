"""Invoker del patrón Command: lee líneas, busca el comando y lo ejecuta.

Los errores de cualquier comando se muestran y se registran en el log; la consola nunca se cae.
"""
from __future__ import annotations

from synthetix.core.app_context import AppContext
from synthetix.core.command_args import CommandArgs
from synthetix.core.command_registry import CommandRegistry


class Console:
    def __init__(self, registry: CommandRegistry, ctx: AppContext) -> None:
        self._registry = registry
        self._ctx = ctx

    def run(self) -> None:
        mascot = r"""
   /\_/\   
  ( o.o )  Synthetix Studio
   > ^ <   Mini IDE por consola
"""
        print(f"\033[38;5;183m{mascot}\033[0m")
        print("\033[90m  Escribe 'help' para ver los comandos.\033[0m\n")
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
            print(f"[error] {e}")
            self._ctx.logger.error(f"{args.name}: {e}")

    def _prompt(self) -> str:
        active = self._ctx.files.active
        if active:
            return f"\033[92msynthetix\033[0m(\033[96m{active.name}\033[0m)> "
        return "\033[92msynthetix\033[0m> "

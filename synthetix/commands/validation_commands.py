"""Comandos del módulo 2: Validación e historial. DUEÑO: Luis Orellana"""
from __future__ import annotations

from synthetix.commands.utils import CommandUtils
from synthetix.core.command import Command
from synthetix.core.command_registry import CommandRegistry
from synthetix.validation.syntax_checker import SyntaxChecker


class CheckCommand(Command):
    name = "check"
    usage = "check"
    description = "Valida el balanceo de (), {}, [] en el código activo"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        result = SyntaxChecker().check(file.content)
        if result.ok:
            print(f"OK: los delimitadores (), {{}} y [] están balanceados en {file.name}.")
            return
        print(f"Desbalance en línea {result.line}, carácter {result.column}: {result.message}")
        lines = file.lines()
        if 1 <= result.line <= len(lines):
            print(f"{result.line:>5} | {lines[result.line - 1]}")
            print("      | " + " " * max(result.column - 1, 0) + "^")


class UndoCommand(Command):
    name = "undo"
    usage = "undo"
    description = "Deshace el último cambio (pila Undo)"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        if not file.undo():
            print("No hay cambios para deshacer.")
            return
        print(f"Cambio deshecho {CommandUtils.history_summary(file)}")


class RedoCommand(Command):
    name = "redo"
    usage = "redo"
    description = "Rehace el cambio deshecho (pila Redo)"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        if not file.redo():
            print("No hay cambios para rehacer.")
            return
        print(f"Cambio rehecho {CommandUtils.history_summary(file)}")


class HistoryCommand(Command):
    name = "history"
    usage = "history"
    description = "Muestra el tamaño de las pilas Undo/Redo"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        print(f"{file.name} {CommandUtils.history_summary(file)}")


class ValidationCommandModule:
    @staticmethod
    def register_into(registry: CommandRegistry) -> None:
        for command in (CheckCommand(), UndoCommand(), RedoCommand(), HistoryCommand()):
            registry.add(command)

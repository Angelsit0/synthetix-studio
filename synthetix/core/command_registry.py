"""Registro de comandos disponibles."""
from __future__ import annotations

from typing import Iterator, Optional

from synthetix.core.command import Command


class CommandRegistry:
    def __init__(self) -> None:
        self._commands: list = []

    def add(self, command: Command) -> None:
        if self.find(command.name) is not None:
            raise ValueError(f"Comando duplicado: {command.name}")
        self._commands.append(command)

    def find(self, name: str) -> Optional[Command]:
        for command in self._commands:
            if command.name == name:
                return command
        return None

    def __iter__(self) -> Iterator[Command]:
        return iter(self._commands)

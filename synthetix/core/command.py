"""Patrón Command: cada acción de la CLI es un objeto con la misma interfaz.

- Console (Invoker) no sabe qué hace cada comando; solo lo busca y llama execute().
- CommandRegistry guarda los comandos disponibles.
- Los receptores son FileManager, CodeFile, SyntaxChecker, SortStrategy, RequestBuffer...
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from synthetix.core.command_args import CommandArgs

if TYPE_CHECKING:
    from synthetix.core.app_context import AppContext


class Command(ABC):
    name = ""
    usage = ""
    description = ""
    min_args = 0  # sin contar el nombre del comando

    @abstractmethod
    def execute(self, args: CommandArgs, ctx: "AppContext") -> None:
        """Ejecuta el comando sobre el contexto de la aplicación."""

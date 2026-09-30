"""Comandos de los módulos 4 y 5: Cola de peticiones e IA. DUEÑO: Alfredo Aureliano"""
from __future__ import annotations

from synthetix.commands.utils import CommandUtils
from synthetix.core.command import Command
from synthetix.core.command_registry import CommandRegistry


class AnalyzeCommand(Command):
    name = "analyze"
    usage = "analyze"
    description = "Encola el código activo para análisis Big O con IA"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        if not ctx.config.api_base_url:
            raise RuntimeError("No hay endpoint configurado (api.base_url en config.json)")
        if not file.content.strip():
            raise RuntimeError("El archivo activo está vacío")
        request_id = ctx.requests.submit(file.name, file.content)
        print(f"Solicitud #{request_id} encolada para {file.name}. "
              "Usa 'queue-status' para ver la cola y 'results' para ver respuestas.")


class QueueStatusCommand(Command):
    name = "queue-status"
    usage = "queue-status"
    description = "Estado de la cola FIFO de peticiones a la IA"

    def execute(self, args, ctx) -> None:
        print(ctx.requests.status_report())


class ResultsCommand(Command):
    name = "results"
    usage = "results"
    description = "Muestra las respuestas de la IA (Big O y refactorización)"

    def execute(self, args, ctx) -> None:
        print(ctx.requests.results_report())


class AICommandModule:
    @staticmethod
    def register_into(registry: CommandRegistry) -> None:
        for command in (AnalyzeCommand(), QueueStatusCommand(), ResultsCommand()):
            registry.add(command)

"""Ayudas compartidas por los comandos."""
from __future__ import annotations

from synthetix.analysis.static_analyzer import StaticAnalyzer
from synthetix.core.app_context import AppContext
from synthetix.files.code_file import CodeFile


class CommandUtils:
    @staticmethod
    def active_file(ctx: AppContext) -> CodeFile:
        if ctx.files.active is None:
            raise RuntimeError("No hay archivo activo. Usa 'new <nombre>' o 'switch <id/nombre>'.")
        return ctx.files.active

    @staticmethod
    def parse_line_number(text: str) -> int:
        if not text.isdigit() or int(text) == 0:
            raise ValueError(f"Número de línea inválido: '{text}'")
        return int(text)

    @staticmethod
    def print_diagnostics(diagnostics: list) -> None:
        if not diagnostics:
            print("Sin diagnósticos: el código no generó alertas.")
            return
        print(f"{'LÍNEA':<7}{'GRAVEDAD':<10}{'REGLA':<24}MENSAJE")
        for d in diagnostics:
            print(f"{d.line:<7}{d.severity_name:<10}{d.rule:<24}{d.message}")

    @staticmethod
    def history_summary(file: CodeFile) -> str:
        return f"(pila undo: {file.history.undo_count} | pila redo: {file.history.redo_count})"

    @staticmethod
    def make_analyzer(ctx: AppContext) -> StaticAnalyzer:
        return StaticAnalyzer(ctx.config.get_int("editor.max_line_length", 100),
                              ctx.config.get_int("editor.max_function_lines", 40))

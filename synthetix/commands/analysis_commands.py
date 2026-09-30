"""Comandos del módulo 3: Motor de ordenamiento. DUEÑOS: Luis (sort) / Angel (lint)"""
from __future__ import annotations

import time

from synthetix.analysis.sorting import DiagnosticComparators, SortStrategyFactory
from synthetix.commands.utils import CommandUtils
from synthetix.core.command import Command
from synthetix.core.command_registry import CommandRegistry


class LintCommand(Command):
    name = "lint"
    usage = "lint"
    description = "Análisis estático: diagnósticos en orden de aparición"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        diagnostics = CommandUtils.make_analyzer(ctx).analyze(file)
        CommandUtils.print_diagnostics(diagnostics)
        print(f"{len(diagnostics)} diagnósticos en {file.name}")


class SortCommand(Command):
    name = "sort"
    usage = "sort <line|severity> <mergesort|shellsort> [asc|desc]"
    description = "Ordena los diagnósticos con algoritmos propios"
    min_args = 2

    def execute(self, args, ctx) -> None:
        criterion, algorithm = args[1], args[2]
        order = args[3] if args.count() > 3 else "asc"
        if order not in ("asc", "desc"):
            raise ValueError(f"Orden desconocido '{order}'. Usa: asc | desc")
        descending = order == "desc"

        if criterion in ("line", "linea"):
            before = (DiagnosticComparators.by_line_desc if descending
                      else DiagnosticComparators.by_line_asc)
        elif criterion in ("severity", "gravedad"):
            before = (DiagnosticComparators.by_severity_desc if descending
                      else DiagnosticComparators.by_severity_asc)
        else:
            raise ValueError(f"Criterio desconocido '{criterion}'. Usa: line | severity")

        strategy = SortStrategyFactory.create(algorithm)
        if strategy is None:
            raise ValueError(f"Algoritmo desconocido '{algorithm}'. Usa: mergesort | shellsort")

        file = CommandUtils.active_file(ctx)
        diagnostics = CommandUtils.make_analyzer(ctx).analyze(file)
        start = time.perf_counter()
        strategy.sort(diagnostics, before)
        elapsed_us = (time.perf_counter() - start) * 1_000_000

        CommandUtils.print_diagnostics(diagnostics)
        print(f"{len(diagnostics)} diagnósticos ordenados por {criterion} ({order}) "
              f"con {strategy.name} en {elapsed_us:.0f} µs")


class AnalysisCommandModule:
    @staticmethod
    def register_into(registry: CommandRegistry) -> None:
        registry.add(LintCommand())
        registry.add(SortCommand())

"""Alertas generadas por el análisis estático. Es lo que ordena el comando sort."""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Severity(IntEnum):
    INFO = 1
    WARNING = 2
    ERROR = 3


@dataclass
class Diagnostic:
    line: int
    severity: Severity
    rule: str      # ej: "line-too-long", "function-too-long"
    message: str   # ej: "La función main tiene 52 líneas (máximo 40)"

    @property
    def severity_name(self) -> str:
        return self.severity.name

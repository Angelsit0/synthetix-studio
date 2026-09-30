"""Balanceo de (), {}, [] con la Stack propia.             DUEÑO: Luis Orellana

Casos a reportar:
  1. Cierre sin apertura:          "se encontró ')' sin apertura"
  2. Cierre que no corresponde:    "se encontró ')' pero se esperaba '}' (abierto en línea X)"
  3. Apertura sin cerrar al final: reportar la línea/columna donde se ABRIÓ
Recomendado: ignorar delimitadores dentro de "cadenas", 'c', # comentarios, // y /* */.
Complejidad esperada: O(n) tiempo, O(n) espacio en el peor caso.
"""
from __future__ import annotations

from dataclasses import dataclass

from synthetix.ds.stack import Stack  # noqa: F401  (la usará la implementación)


@dataclass
class SyntaxResult:
    ok: bool = True
    line: int = 0     # 1-based
    column: int = 0   # 1-based
    message: str = ""


class SyntaxChecker:
    def check(self, code: str) -> SyntaxResult:
        # Pista: recorrer carácter por carácter llevando línea y columna; apilar
        # (símbolo, línea, columna) en cada apertura y comparar con el tope en cada cierre.
        raise NotImplementedError("[sin implementar] SyntaxChecker.check")

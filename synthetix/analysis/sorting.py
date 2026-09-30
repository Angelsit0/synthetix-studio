"""Motor de ordenamiento: algoritmos propios con patrón Strategy.

La list de Python se usa SOLO como arreglo (acceso por índice). Prohibido usar el
método de ordenamiento de list o la función integrada equivalente.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional

from synthetix.analysis.diagnostic import Diagnostic

# before(a, b) -> True si a debe quedar ANTES que b en el resultado.
Comparator = Callable[[Diagnostic, Diagnostic], bool]


class SortStrategy(ABC):
    name = ""

    @abstractmethod
    def sort(self, items: list, before: Comparator) -> None:
        """Ordena items IN-PLACE (modifica la misma lista)."""


class MergeSort(SortStrategy):
    """DUEÑO: Luis Orellana. O(n log n) en todos los casos, ESTABLE, O(n) memoria extra.

    Pista: recursivo top-down; al mezclar, toma de la izquierda cuando
    not before(derecha, izquierda) para que sea estable.
    """
    name = "mergesort"

    def sort(self, items: list, before: Comparator) -> None:
        if len(items) <= 1:
            return
            
        mid = len(items) // 2
        left = items[:mid]
        right = items[mid:]
        
        self.sort(left, before)
        self.sort(right, before)
        
        i = j = k = 0
        while i < len(left) and j < len(right):
            if before(right[j], left[i]):
                items[k] = right[j]
                j += 1
            else:
                items[k] = left[i]
                i += 1
            k += 1
            
        while i < len(left):
            items[k] = left[i]
            i += 1
            k += 1
            
        while j < len(right):
            items[k] = right[j]
            j += 1
            k += 1


class ShellSort(SortStrategy):
    """DUEÑO: Luis Orellana. Gaps de Knuth (1, 4, 13, 40...): O(n^1.5) peor caso,
    in-place, NO estable.

    Pista: h = 1; mientras h < n // 3: h = 3h + 1; inserción con salto h; h //= 3.
    """
    name = "shellsort"

    def sort(self, items: list, before: Comparator) -> None:
        n = len(items)
        if n <= 1:
            return
            
        h = 1
        while h < n // 3:
            h = 3 * h + 1
            
        while h >= 1:
            for i in range(h, n):
                temp = items[i]
                j = i
                while j >= h and before(temp, items[j - h]):
                    items[j] = items[j - h]
                    j -= h
                items[j] = temp
            h //= 3


class DiagnosticComparators:
    """Criterios de orden disponibles para el comando sort."""

    @staticmethod
    def by_line_asc(a: Diagnostic, b: Diagnostic) -> bool:
        if a.line != b.line:
            return a.line < b.line
        return a.severity > b.severity  # misma línea: lo más grave primero

    @staticmethod
    def by_line_desc(a: Diagnostic, b: Diagnostic) -> bool:
        if a.line != b.line:
            return a.line > b.line
        return a.severity > b.severity

    @staticmethod
    def by_severity_asc(a: Diagnostic, b: Diagnostic) -> bool:
        if a.severity != b.severity:
            return a.severity < b.severity
        return a.line < b.line

    @staticmethod
    def by_severity_desc(a: Diagnostic, b: Diagnostic) -> bool:
        if a.severity != b.severity:
            return a.severity > b.severity
        return a.line < b.line


class SortStrategyFactory:
    @staticmethod
    def create(name: str) -> Optional[SortStrategy]:
        if name == "mergesort":
            return MergeSort()
        if name == "shellsort":
            return ShellSort()
        return None

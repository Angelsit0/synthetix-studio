"""Undo/Redo con DOS pilas independientes.                 DUEÑO: Luis Orellana

Guarda "fotos" completas del texto (patrón Memento). Cada CodeFile tiene uno.
Como cada foto es una copia del texto, la memoria crece O(k·L) con k cambios; por eso
max_states (editor.max_history en config.json) limita cuántos estados se guardan en
Undo: al pasarse, se descartan los más antiguos. 0 = sin límite.
"""
from __future__ import annotations

from synthetix.ds.stack import Stack


class History:
    def __init__(self, max_states: int = 0) -> None:
        self._undo = Stack()
        self._redo = Stack()
        self.max_states = max_states

    def record(self, previous_state: str) -> None:
        """Se llama ANTES de modificar: apila el estado anterior en Undo y vacía Redo.
        Si se supera max_states, se descartan los estados más antiguos."""
        self._undo.push(previous_state)
        self._redo.clear()
        if self.max_states > 0:
            self._undo.truncate(self.max_states)

    def undo(self, current_state: str) -> str:
        """Devuelve el estado a restaurar; el estado actual pasa a la pila Redo."""
        if not self.can_undo():
            return current_state
        self._redo.push(current_state)
        return self._undo.pop()

    def redo(self, current_state: str) -> str:
        """Devuelve el estado a restaurar; el estado actual pasa a la pila Undo."""
        if not self.can_redo():
            return current_state
        self._undo.push(current_state)
        return self._redo.pop()

    def can_undo(self) -> bool:
        return not self._undo.is_empty()

    def can_redo(self) -> bool:
        return not self._redo.is_empty()

    @property
    def undo_count(self) -> int:
        return len(self._undo)

    @property
    def redo_count(self) -> int:
        return len(self._redo)

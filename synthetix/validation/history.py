"""Undo/Redo con DOS pilas independientes.                 DUEÑO: Luis Orellana

Guarda "fotos" completas del texto (patrón Memento). Cada CodeFile tiene uno.
"""
from __future__ import annotations

from synthetix.ds.stack import Stack


class History:
    def __init__(self) -> None:
        self._undo = Stack()
        self._redo = Stack()

    def record(self, previous_state: str) -> None:
        """Se llama ANTES de modificar: apila el estado anterior en Undo y vacía Redo."""
        # TODO(Luis): self._undo.push(previous_state); self._redo.clear()
        # Se deja vacío a propósito para que las ediciones funcionen mientras tanto.
        pass

    def undo(self, current_state: str) -> str:
        """Devuelve el estado a restaurar; el estado actual pasa a la pila Redo."""
        raise NotImplementedError("[sin implementar] History.undo")

    def redo(self, current_state: str) -> str:
        """Devuelve el estado a restaurar; el estado actual pasa a la pila Undo."""
        raise NotImplementedError("[sin implementar] History.redo")

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

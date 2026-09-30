"""Pila LIFO propia con nodos enlazados.                   DUEÑO: Luis Orellana

La usan SyntaxChecker (validar delimitadores) e History (undo/redo).
NO se permite usar una list de Python con append/pop por debajo.
"""
from __future__ import annotations

from typing import Any, Optional


class _Node:
    __slots__ = ("value", "next")

    def __init__(self, value: Any, next_node: Optional[_Node]) -> None:
        self.value = value
        self.next = next_node


class Stack:
    def __init__(self) -> None:
        self._top: Optional[_Node] = None
        self._size = 0

    def push(self, value: Any) -> None:
        """Apila. Esperado O(1)."""
        self._top = _Node(value, self._top)
        self._size += 1

    def pop(self) -> Any:
        """Desapila y devuelve el tope. O(1). IndexError si está vacía."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        value = self._top.value
        self._top = self._top.next
        self._size -= 1
        return value

    def peek(self) -> Any:
        """Consulta el tope sin sacarlo. O(1). IndexError si está vacía."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._top.value

    def clear(self) -> None:
        """Vacía la pila. O(n)."""
        current = self._top
        while current:
            next_node = current.next
            current.next = None
            current = next_node
        self._top = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

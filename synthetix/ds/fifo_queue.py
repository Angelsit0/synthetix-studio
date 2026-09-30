"""Cola FIFO propia con nodos enlazados (_front y _back).  DUEÑO: Alfredo Aureliano

La usa RequestBuffer para las peticiones a la IA.
OJO: la cola NO es thread-safe por sí sola; RequestBuffer la protege con un Lock.
"""
from __future__ import annotations

from typing import Any, Iterator, Optional


class _Node:
    __slots__ = ("value", "next")

    def __init__(self, value: Any) -> None:
        self.value = value
        self.next: Optional[_Node] = None


class Queue:
    def __init__(self) -> None:
        self._front: Optional[_Node] = None
        self._back: Optional[_Node] = None
        self._size = 0

    def enqueue(self, value: Any) -> None:
        """Encola al final. Esperado O(1)."""
        raise NotImplementedError("[sin implementar] Queue.enqueue")

    def dequeue(self) -> Any:
        """Saca y devuelve el primero. O(1). IndexError si está vacía."""
        raise NotImplementedError("[sin implementar] Queue.dequeue")

    def front(self) -> Any:
        """Consulta el primero sin sacarlo. O(1)."""
        raise NotImplementedError("[sin implementar] Queue.front")

    def __iter__(self) -> Iterator[Any]:
        """Recorre del frente al final (para queue-status). O(n)."""
        raise NotImplementedError("[sin implementar] Queue.__iter__")

    def clear(self) -> None:
        raise NotImplementedError("[sin implementar] Queue.clear")

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

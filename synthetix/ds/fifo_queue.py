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
        """Encola al final. O(1): se engancha detrás de _back, sin recorrer."""
        node = _Node(value)
        if self._back is None:
            # Cola vacía: el nuevo nodo es a la vez el primero y el último.
            self._front = node
            self._back = node
        else:
            self._back.next = node
            self._back = node
        self._size += 1

    def dequeue(self) -> Any:
        """Saca y devuelve el primero. O(1). IndexError si está vacía."""
        if self._front is None:
            raise IndexError("No se puede desencolar: la cola está vacía")
        node = self._front
        self._front = node.next
        if self._front is None:
            # Se sacó el último: _back no puede seguir apuntando a un nodo que ya no está.
            self._back = None
        value = node.value
        node.next = None    # desenlazar el nodo sacado para liberarlo
        node.value = None
        self._size -= 1
        return value

    def front(self) -> Any:
        """Consulta el primero sin sacarlo. O(1). IndexError si está vacía."""
        if self._front is None:
            raise IndexError("No se puede consultar el frente: la cola está vacía")
        return self._front.value

    def __iter__(self) -> Iterator[Any]:
        """Recorre del frente al final (para queue-status). O(n)."""
        current = self._front
        while current is not None:
            yield current.value
            current = current.next

    def clear(self) -> None:
        """Desenlaza todos los nodos. O(n)."""
        current = self._front
        while current is not None:
            following = current.next    # se guarda antes de cortar el enlace
            current.next = None
            current.value = None
            current = following
        self._front = None
        self._back = None
        self._size = 0

    def __len__(self) -> int:
        """Cantidad de elementos. O(1): se lleva el contador _size."""
        return self._size

    def is_empty(self) -> bool:
        """True si no hay elementos. O(1)."""
        return self._size == 0

"""Lista doblemente enlazada propia.                      DUEÑO: Angel Torres

La usa FileManager para guardar los archivos abiertos de la sesión.
Al implementar cada método, deja en su docstring la complejidad (va al informe).
"""
from __future__ import annotations

from typing import Any, Callable, Iterator, Optional


class _Node:
    __slots__ = ("value", "prev", "next")

    def __init__(self, value: Any) -> None:
        self.value = value
        self.prev: Optional[_Node] = None
        self.next: Optional[_Node] = None


class LinkedList:
    def __init__(self) -> None:
        self._head: Optional[_Node] = None
        self._tail: Optional[_Node] = None
        self._size = 0

    def push_back(self, value: Any) -> None:
        """Inserta al final. Esperado: O(1) usando _tail."""
        raise NotImplementedError("[sin implementar] LinkedList.push_back")

    def remove_at(self, index: int) -> bool:
        """Elimina el nodo en la posición index (0-based). O(n).

        'Liberar' el nodo en Python = desenlazarlo por completo (prev/next = None)
        para que no quede ninguna referencia y el recolector de basura lo elimine.
        Devuelve False si la posición no existe.
        """
        raise NotImplementedError("[sin implementar] LinkedList.remove_at")

    def at(self, index: int) -> Any:
        """Valor en la posición index (0-based). O(n). IndexError si no existe."""
        raise NotImplementedError("[sin implementar] LinkedList.at")

    def index_of(self, predicate: Callable[[Any], bool]) -> int:
        """Posición del primer valor que cumple predicate, o -1. O(n)."""
        raise NotImplementedError("[sin implementar] LinkedList.index_of")

    def __iter__(self) -> Iterator[Any]:
        """Recorre de head a tail (permite: for archivo in lista). O(n)."""
        raise NotImplementedError("[sin implementar] LinkedList.__iter__")

    def clear(self) -> None:
        """Desenlaza todos los nodos. O(n)."""
        raise NotImplementedError("[sin implementar] LinkedList.clear")

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

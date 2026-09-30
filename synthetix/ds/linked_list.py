"""Lista doblemente enlazada propia.                      DUEÑO: Angel Torres

La usa FileManager para guardar los archivos abiertos de la sesión.
Al implementar cada método, deja en su docstring la complejidad (va al informe).

Por qué doble y no simple: cada nodo conoce a su anterior, así que al eliminar un nodo
se re-enlazan sus vecinos directamente sin volver a recorrer la lista para buscar el
anterior, y con _tail se inserta al final en O(1).
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
        """Inserta al final. O(1): se usa _tail, no hace falta recorrer la lista."""
        node = _Node(value)
        if self._tail is None:
            # Lista vacía: el nuevo nodo es a la vez el primero y el último.
            self._head = node
            self._tail = node
        else:
            # Se engancha detrás del último y pasa a ser el nuevo último.
            node.prev = self._tail
            self._tail.next = node
            self._tail = node
        self._size += 1

    def remove_at(self, index: int) -> bool:
        """Elimina el nodo en la posición index (0-based). O(n) por buscar el nodo;
        el re-enlace en sí es O(1).

        'Liberar' el nodo en Python = desenlazarlo por completo (prev/next = None)
        para que no quede ninguna referencia y el recolector de basura lo elimine.
        Devuelve False si la posición no existe.
        """
        node = self._node_at(index)
        if node is None:
            return False

        # Enlace hacia adelante: quien apuntaba al nodo ahora apunta a su siguiente.
        if node.prev is None:
            self._head = node.next          # era el primero
        else:
            node.prev.next = node.next      # medio o último

        # Enlace hacia atrás: quien venía después ahora apunta al anterior del nodo.
        if node.next is None:
            self._tail = node.prev          # era el último
        else:
            node.next.prev = node.prev      # primero o medio

        # Si era el único nodo, las dos ramas dejan _head y _tail en None.
        # Liberar: se cortan todas sus referencias.
        node.prev = None
        node.next = None
        node.value = None
        self._size -= 1
        return True

    def at(self, index: int) -> Any:
        """Valor en la posición index (0-based). O(n). IndexError si no existe."""
        node = self._node_at(index)
        if node is None:
            raise IndexError(f"Posición fuera de rango: {index} (hay {self._size} elementos)")
        return node.value

    def index_of(self, predicate: Callable[[Any], bool]) -> int:
        """Posición del primer valor que cumple predicate, o -1. O(n)."""
        position = 0
        current = self._head
        while current is not None:
            if predicate(current.value):
                return position
            current = current.next
            position += 1
        return -1

    def __iter__(self) -> Iterator[Any]:
        """Recorre de head a tail (permite: for archivo in lista). O(n)."""
        current = self._head
        while current is not None:
            yield current.value
            current = current.next

    def clear(self) -> None:
        """Desenlaza todos los nodos. O(n)."""
        current = self._head
        while current is not None:
            following = current.next    # se guarda antes de cortar el enlace
            current.prev = None
            current.next = None
            current.value = None
            current = following
        self._head = None
        self._tail = None
        self._size = 0

    def __len__(self) -> int:
        """Cantidad de elementos. O(1): se lleva el contador _size."""
        return self._size

    def is_empty(self) -> bool:
        """True si no hay elementos. O(1)."""
        return self._size == 0

    def _node_at(self, index: int) -> Optional[_Node]:
        """Nodo en la posición index, o None si no existe. O(n).

        Como la lista es doble, si el índice está en la segunda mitad se recorre
        desde _tail hacia atrás: en el peor caso se visitan n/2 nodos.
        """
        if index < 0 or index >= self._size:
            return None
        if index < self._size // 2:
            current = self._head
            for _ in range(index):
                current = current.next
        else:
            current = self._tail
            for _ in range(self._size - 1 - index):
                current = current.prev
        return current

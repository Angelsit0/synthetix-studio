"""Archivos abiertos sobre la LinkedList propia.            DUEÑO: Angel Torres"""
from __future__ import annotations

from typing import Iterator, Optional

from synthetix.ds.linked_list import LinkedList
from synthetix.files.code_file import CodeFile


class FileManager:
    def __init__(self) -> None:
        self._files = LinkedList()
        self._active: Optional[CodeFile] = None
        self._next_id = 1

    def create(self, name: str, content: str) -> CodeFile:
        """Crea el archivo, lo agrega al final de la lista y lo deja activo.

        Lanza ValueError si ya existe uno con ese nombre.
        Pista: validar con self._files.index_of(lambda f: f.name == name), luego
        CodeFile(self._next_id, name, content), push_back, _next_id += 1, _active = archivo.
        """
        raise NotImplementedError("[sin implementar] FileManager.create")

    def find(self, id_or_name: str) -> Optional[CodeFile]:
        """Busca por id numérico ("2") o por nombre ("main.py"). None si no existe."""
        raise NotImplementedError("[sin implementar] FileManager.find")

    def switch_to(self, id_or_name: str) -> bool:
        """Cambia el archivo activo. False si no existe."""
        raise NotImplementedError("[sin implementar] FileManager.switch_to")

    def remove(self, id_or_name: str) -> bool:
        """Elimina el archivo y libera su nodo. Si era el activo, el activo pasa
        al siguiente (o al anterior, o None si la lista queda vacía)."""
        raise NotImplementedError("[sin implementar] FileManager.remove")

    @property
    def active(self) -> Optional[CodeFile]:
        return self._active

    def count(self) -> int:
        return len(self._files)

    def __iter__(self) -> Iterator[CodeFile]:
        return iter(self._files)

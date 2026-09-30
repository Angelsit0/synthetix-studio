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
        """Crea el archivo, lo agrega al final de la lista y lo deja activo. O(n).

        O(n) porque antes de insertar se recorre la lista para comprobar que el nombre
        no exista; la inserción en sí (push_back) es O(1).
        Lanza ValueError si el nombre está vacío o si ya existe uno con ese nombre.
        """
        if not name.strip():
            raise ValueError("El nombre del archivo no puede estar vacío")
        if self._files.index_of(lambda f: f.name == name) != -1:
            raise ValueError(f"Ya existe un archivo llamado '{name}'")
        file = CodeFile(self._next_id, name, content)
        self._files.push_back(file)
        self._next_id += 1
        self._active = file
        return file

    def find(self, id_or_name: str) -> Optional[CodeFile]:
        """Busca por id numérico ("2") o por nombre ("main.py"). None si no existe. O(n)."""
        position = self._position_of(id_or_name)
        if position == -1:
            return None
        return self._files.at(position)

    def switch_to(self, id_or_name: str) -> bool:
        """Cambia el archivo activo. False si no existe. O(n) por la búsqueda."""
        file = self.find(id_or_name)
        if file is None:
            return False
        self._active = file
        return True

    def remove(self, id_or_name: str) -> bool:
        """Elimina el archivo y libera su nodo. Si era el activo, el activo pasa
        al siguiente (o al anterior, o None si la lista queda vacía). O(n).

        El nuevo activo se calcula ANTES de borrar, mientras las posiciones
        pos + 1 y pos - 1 todavía son los vecinos del archivo eliminado.
        """
        position = self._position_of(id_or_name)
        if position == -1:
            return False
        file = self._files.at(position)
        if file is self._active:
            if position + 1 < len(self._files):
                self._active = self._files.at(position + 1)   # el siguiente
            elif position > 0:
                self._active = self._files.at(position - 1)   # el anterior
            else:
                self._active = None                           # era el único
        return self._files.remove_at(position)

    @property
    def active(self) -> Optional[CodeFile]:
        return self._active

    def count(self) -> int:
        """Cantidad de archivos abiertos. O(1)."""
        return len(self._files)

    def __iter__(self) -> Iterator[CodeFile]:
        """Recorre los archivos en el orden en que se abrieron. O(n)."""
        return iter(self._files)

    def _position_of(self, id_or_name: str) -> int:
        """Posición del archivo en la lista, o -1. O(n).

        Si el texto es un número se busca primero como id; si no aparece, se busca
        como nombre (así también se encuentra un archivo que se llame, por ejemplo, "2").
        """
        if id_or_name.isdigit():
            file_id = int(id_or_name)
            position = self._files.index_of(lambda f: f.id == file_id)
            if position != -1:
                return position
        return self._files.index_of(lambda f: f.name == id_or_name)

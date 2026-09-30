"""Un archivo o fragmento de código abierto en la sesión.

Cada archivo tiene su propio historial Undo/Redo.
TODA modificación del texto debe pasar por apply_edit().
"""
from __future__ import annotations

from synthetix.validation.history import History


class CodeFile:
    def __init__(self, file_id: int, name: str, content: str) -> None:
        self.id = file_id
        self.name = name
        self._content = content
        self.modified = False
        self.history = History()

    @property
    def content(self) -> str:
        return self._content

    def mark_saved(self) -> None:
        self.modified = False

    def apply_edit(self, new_content: str) -> None:
        """Reemplaza el contenido guardando el estado anterior en la pila Undo."""
        if new_content == self._content:
            return
        self.history.record(self._content)
        self._content = new_content
        self.modified = True

    def undo(self) -> bool:
        if not self.history.can_undo():
            return False
        self._content = self.history.undo(self._content)
        self.modified = True
        return True

    def redo(self) -> bool:
        if not self.history.can_redo():
            return False
        self._content = self.history.redo(self._content)
        self.modified = True
        return True

    def lines(self) -> list:
        return self._content.splitlines()

    def line_count(self) -> int:
        return len(self.lines())

    def append_line(self, text: str) -> None:
        current = self.lines()
        current.append(text)
        self.apply_edit(self._join(current))

    def insert_line(self, line_number: int, text: str) -> None:
        current = self.lines()
        self._check_line(line_number, len(current) + 1)
        current.insert(line_number - 1, text)
        self.apply_edit(self._join(current))

    def replace_line(self, line_number: int, text: str) -> None:
        current = self.lines()
        self._check_line(line_number, len(current))
        current[line_number - 1] = text
        self.apply_edit(self._join(current))

    def remove_line(self, line_number: int) -> None:
        current = self.lines()
        self._check_line(line_number, len(current))
        del current[line_number - 1]
        self.apply_edit(self._join(current))

    @staticmethod
    def _join(lines: list) -> str:
        return "".join(line + "\n" for line in lines)

    @staticmethod
    def _check_line(line_number: int, maximum: int) -> None:
        if line_number < 1 or line_number > maximum:
            raise IndexError(f"Línea fuera de rango: {line_number} (válido: 1..{maximum})")

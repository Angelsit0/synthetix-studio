"""Genera diagnósticos del archivo activo.                  DUEÑO: Angel Torres

Reglas implementadas (8), pensadas para código Python (funciones con def):
  ERROR   unbalanced-delimiters  reutiliza SyntaxChecker de Luis
  WARNING function-too-long      la función supera editor.max_function_lines
  WARNING line-too-long          la línea supera editor.max_line_length
  WARNING wildcard-import        'from x import *'
  WARNING deep-nesting           más de 4 niveles de indentación (uno por bloque)
  INFO    function-lines         una línea informativa por función con su conteo de líneas
  INFO    todo-comment           comentarios TODO / FIXME
  INFO    trailing-whitespace    espacios al final de la línea
Devuelve los diagnósticos en el orden en que aparecen (SIN ordenar): ordenar es trabajo
del comando sort con MergeSort / ShellSort.
"""
from __future__ import annotations

from typing import Optional

from synthetix.analysis.diagnostic import Diagnostic, Severity
from synthetix.files.code_file import CodeFile
from synthetix.validation.syntax_checker import SyntaxChecker, SyntaxResult

# Un nivel de indentación son 4 espacios (PEP 8); un tab cuenta como un nivel.
_SPACES_PER_LEVEL = 4
_MAX_NESTING = 4


class StaticAnalyzer:
    def __init__(self, max_line_length: int, max_function_lines: int) -> None:
        self._max_line_length = max_line_length
        self._max_function_lines = max_function_lines

    def analyze(self, file: CodeFile) -> list:
        """Recorre el archivo UNA vez, de arriba abajo, aplicando las reglas a cada línea.

        Complejidad: O(C), con C = total de caracteres, porque cada línea se revisa un
        número constante de veces. La única excepción es medir el largo de cada función,
        que recorre su cuerpo; con funciones anidadas a profundidad p eso da O(p·C) en el
        peor caso (en código normal p es pequeño). Espacio: O(d) para los d diagnósticos.
        """
        lines = file.lines()
        diagnostics = []                     # arreglo simple: lo ordena luego el sort
        delimiter_error = self._check_delimiters(file.content)
        previous_level = 0                   # nivel de la última línea no vacía

        for index in range(len(lines)):
            text = lines[index]
            number = index + 1               # las líneas se muestran desde 1

            if delimiter_error is not None and delimiter_error.line == number:
                diagnostics.append(Diagnostic(number, Severity.ERROR, "unbalanced-delimiters",
                                              delimiter_error.message))
            self._check_function(lines, index, diagnostics)
            self._check_line_length(text, number, diagnostics)
            self._check_wildcard_import(text, number, diagnostics)
            if text.strip():
                previous_level = self._check_nesting(text, number, previous_level, diagnostics)
            self._check_todo(text, number, diagnostics)
            self._check_trailing_whitespace(text, number, diagnostics)
        return diagnostics

    # ------------------------------------------------------------------ reglas

    @staticmethod
    def _check_delimiters(code: str) -> Optional[SyntaxResult]:
        """ERROR unbalanced-delimiters: usa el SyntaxChecker (pila) de Luis.

        Devuelve el resultado solo si hay error, para emitirlo al llegar a su línea.
        Mientras SyntaxChecker no esté implementado en esta rama, la regla se omite
        en lugar de romper todo el análisis.
        """
        try:
            result = SyntaxChecker().check(code)
        except NotImplementedError:
            return None
        if result.ok:
            return None
        return result

    def _check_function(self, lines: list, index: int, diagnostics: list) -> None:
        """INFO function-lines y WARNING function-too-long si la línea abre una función."""
        name = self._function_name(lines[index])
        if name is None:
            return
        end = self._function_end(lines, index)
        length = end - index + 1
        number = index + 1
        diagnostics.append(Diagnostic(number, Severity.INFO, "function-lines",
                                      f"La función {name} tiene {length} líneas"))
        if length > self._max_function_lines:
            diagnostics.append(Diagnostic(
                number, Severity.WARNING, "function-too-long",
                f"La función {name} tiene {length} líneas (máximo {self._max_function_lines})"))

    def _check_line_length(self, text: str, number: int, diagnostics: list) -> None:
        """WARNING line-too-long."""
        if len(text) > self._max_line_length:
            diagnostics.append(Diagnostic(
                number, Severity.WARNING, "line-too-long",
                f"La línea tiene {len(text)} caracteres (máximo {self._max_line_length})"))

    @staticmethod
    def _check_wildcard_import(text: str, number: int, diagnostics: list) -> None:
        """WARNING wildcard-import: 'from modulo import *' esconde de dónde viene cada nombre."""
        stripped = text.strip()
        if stripped.startswith("from ") and stripped.endswith("import *"):
            diagnostics.append(Diagnostic(number, Severity.WARNING, "wildcard-import",
                                          "Importación con '*': importa solo lo que uses"))

    def _check_nesting(self, text: str, number: int, previous_level: int,
                       diagnostics: list) -> int:
        """WARNING deep-nesting, UNO por bloque: solo cuando la indentación pasa por
        encima del límite (la línea anterior no vacía estaba dentro del límite).
        Devuelve el nivel de esta línea para compararlo con la siguiente.
        """
        level = self._indent_width(text) // _SPACES_PER_LEVEL
        if level > _MAX_NESTING and previous_level <= _MAX_NESTING:
            diagnostics.append(Diagnostic(
                number, Severity.WARNING, "deep-nesting",
                f"Bloque con {level} niveles de indentación (máximo {_MAX_NESTING})"))
        return level

    @staticmethod
    def _check_todo(text: str, number: int, diagnostics: list) -> None:
        """INFO todo-comment: TODO o FIXME dentro de un comentario '#'."""
        hash_position = text.find("#")
        if hash_position == -1:
            return
        comment = text[hash_position:].upper()
        if "TODO" in comment or "FIXME" in comment:
            diagnostics.append(Diagnostic(number, Severity.INFO, "todo-comment",
                                          "Comentario pendiente: " + text[hash_position:].strip()))

    @staticmethod
    def _check_trailing_whitespace(text: str, number: int, diagnostics: list) -> None:
        """INFO trailing-whitespace: espacios o tabs al final de la línea."""
        if text.endswith(" ") or text.endswith("\t"):
            diagnostics.append(Diagnostic(number, Severity.INFO, "trailing-whitespace",
                                          "Espacios en blanco al final de la línea"))

    # ------------------------------------------------------------------ ayudas

    @staticmethod
    def _function_name(text: str) -> Optional[str]:
        """Nombre de la función si la línea es 'def nombre(' o 'async def nombre('."""
        stripped = text.strip()
        if stripped.startswith("async def "):
            stripped = stripped[len("async "):]
        if not stripped.startswith("def "):
            return None
        parenthesis = stripped.find("(")
        if parenthesis == -1:
            return None
        return stripped[len("def "):parenthesis].strip()

    def _function_end(self, lines: list, start: int) -> int:
        """Índice de la última línea de la función que empieza en start. O(largo de la función).

        El cuerpo son las líneas con MÁS indentación que el def; las líneas vacías no
        cortan la función, pero tampoco cuentan si quedan al final.
        """
        def_indent = self._indent_width(lines[start])
        end = start
        index = start + 1
        while index < len(lines):
            text = lines[index]
            if text.strip():
                if self._indent_width(text) <= def_indent:
                    break                    # se volvió al nivel del def: terminó
                end = index
            index += 1
        return end

    @staticmethod
    def _indent_width(text: str) -> int:
        """Espacios al inicio de la línea (un tab cuenta como 4)."""
        width = 0
        for char in text:
            if char == " ":
                width += 1
            elif char == "\t":
                width += _SPACES_PER_LEVEL
            else:
                break
        return width

"""Genera diagnósticos del archivo activo.                  DUEÑO: Angel Torres

Reglas sugeridas (mínimo 5 para que el sort tenga datos interesantes):
  ERROR   unbalanced-delimiters  (reusar SyntaxChecker de Luis)
  WARNING function-too-long      conteo de líneas por función (editor.max_function_lines)
  WARNING line-too-long          (editor.max_line_length)
  WARNING wildcard-import        'from x import *'
  WARNING deep-nesting           más de 4 niveles de indentación
  INFO    todo-comment           comentarios TODO / FIXME
  INFO    trailing-whitespace    espacios al final de la línea
  INFO    function-lines         una línea informativa por función con su conteo de líneas
Debe detectar funciones tanto de Python (def) como de C/C++ (llaves), o al menos de uno.
Devuelve los diagnósticos en el orden en que aparecen (SIN ordenar).
"""
from __future__ import annotations

from synthetix.files.code_file import CodeFile


class StaticAnalyzer:
    def __init__(self, max_line_length: int, max_function_lines: int) -> None:
        self._max_line_length = max_line_length
        self._max_function_lines = max_function_lines

    def analyze(self, file: CodeFile) -> list:
        raise NotImplementedError("[sin implementar] StaticAnalyzer.analyze")

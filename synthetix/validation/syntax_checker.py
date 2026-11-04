"""Balanceo de (), {}, [] con la Stack propia.             DUEÑO: Luis Orellana

Casos a reportar:
  1. Cierre sin apertura:          "se encontró ')' sin apertura"
  2. Cierre que no corresponde:    "se encontró ')' pero se esperaba '}' (abierto en línea X)"
  3. Apertura sin cerrar al final: reportar la línea/columna donde se ABRIÓ
Se ignoran los delimitadores dentro de cadenas y de # comentarios:
  - "..." y '...' terminan, a más tardar, al final de su línea (en Python no cruzan
    líneas salvo con una barra invertida al final). Así una comilla sin cerrar no
    esconde los errores de las líneas siguientes.
  - \"\"\"...\"\"\" y '''...''' (docstrings) pueden ocupar varias líneas.
No se tratan // ni /* */ como comentarios: en Python // es la división entera.
Dentro de una cadena, la barra invertida escapa el carácter siguiente ("a\\"(b").
Complejidad: O(n) tiempo, O(n) espacio en el peor caso (n = caracteres del código).
"""
from __future__ import annotations

from dataclasses import dataclass

from synthetix.ds.stack import Stack

_OPENING_FOR = {')': '(', '}': '{', ']': '['}
_CLOSING_FOR = {'(': ')', '{': '}', '[': ']'}


@dataclass
class SyntaxResult:
    ok: bool = True
    line: int = 0     # 1-based
    column: int = 0   # 1-based
    message: str = ""


class SyntaxChecker:
    def check(self, code: str) -> SyntaxResult:
        stack = Stack()
        string_delim = ""   # "" fuera de cadena; si no: '"', "'", '\"\"\"' o "'''"

        for line_idx, line in enumerate(code.split('\n')):
            number = line_idx + 1
            length = len(line)
            continues_next_line = False
            col = 0
            while col < length:
                char = line[col]

                if string_delim:
                    if char == '\\':
                        # La barra invertida y el carácter siguiente se saltan juntos,
                        # así \" no cierra la cadena. Al final de la línea, la continúa.
                        continues_next_line = col + 1 >= length
                        col += 2
                        continue
                    if line.startswith(string_delim, col):
                        col += len(string_delim)
                        string_delim = ""
                        continue
                    col += 1
                    continue

                if char == '#':
                    break                           # comentario: el resto de la línea no cuenta
                if char in "\"'":
                    triple = char * 3
                    string_delim = triple if line.startswith(triple, col) else char
                    col += len(string_delim)
                    continue
                if char in "({[":
                    stack.push((char, number, col + 1))
                elif char in ")}]":
                    if stack.is_empty():
                        return SyntaxResult(False, number, col + 1,
                                            f"se encontró '{char}' sin apertura")
                    top_char, top_line, _ = stack.pop()
                    if top_char != _OPENING_FOR[char]:
                        return SyntaxResult(False, number, col + 1,
                                            f"se encontró '{char}' pero se esperaba "
                                            f"'{_CLOSING_FOR[top_char]}' (abierto en línea {top_line})")
                col += 1

            # Una cadena de comillas simples no cruza líneas (salvo con \ al final).
            if len(string_delim) == 1 and not continues_next_line:
                string_delim = ""

        if not stack.is_empty():
            top_char, top_line, top_col = stack.pop()
            return SyntaxResult(False, top_line, top_col, f"Apertura '{top_char}' sin cerrar")

        return SyntaxResult(True, 0, 0, "OK")

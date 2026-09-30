"""Balanceo de (), {}, [] con la Stack propia.             DUEÑO: Luis Orellana

Casos a reportar:
  1. Cierre sin apertura:          "se encontró ')' sin apertura"
  2. Cierre que no corresponde:    "se encontró ')' pero se esperaba '}' (abierto en línea X)"
  3. Apertura sin cerrar al final: reportar la línea/columna donde se ABRIÓ
Recomendado: ignorar delimitadores dentro de "cadenas", 'c', # comentarios, // y /* */.
Complejidad esperada: O(n) tiempo, O(n) espacio en el peor caso.
"""
from __future__ import annotations

from dataclasses import dataclass

from synthetix.ds.stack import Stack  # noqa: F401  (la usará la implementación)


@dataclass
class SyntaxResult:
    ok: bool = True
    line: int = 0     # 1-based
    column: int = 0   # 1-based
    message: str = ""


class SyntaxChecker:
    def check(self, code: str) -> SyntaxResult:
        stack = Stack()
        pairs = {')': '(', '}': '{', ']': '['}
        reverse_pairs = {'(': ')', '{': '}', '[': ']'}
        
        lines = code.split('\n')
        
        in_string = False
        string_char = ''
        in_block_comment = False
        
        for line_idx, line in enumerate(lines):
            in_line_comment = False
            col_idx = 0
            while col_idx < len(line):
                char = line[col_idx]
                
                # Handling strings
                if not in_line_comment and not in_block_comment:
                    if char in "\"'":
                        if in_string and string_char == char:
                            in_string = False
                        elif not in_string:
                            in_string = True
                            string_char = char
                            
                # Handling comments
                if not in_string and not in_block_comment and not in_line_comment:
                    if char == '#':
                        in_line_comment = True
                    elif char == '/' and col_idx + 1 < len(line) and line[col_idx+1] == '/':
                        in_line_comment = True
                        col_idx += 1
                    elif char == '/' and col_idx + 1 < len(line) and line[col_idx+1] == '*':
                        in_block_comment = True
                        col_idx += 1
                elif in_block_comment:
                    if char == '*' and col_idx + 1 < len(line) and line[col_idx+1] == '/':
                        in_block_comment = False
                        col_idx += 1
                        
                if not in_string and not in_line_comment and not in_block_comment:
                    if char in "({[":
                        stack.push((char, line_idx + 1, col_idx + 1))
                    elif char in ")}]":
                        if stack.is_empty():
                            return SyntaxResult(False, line_idx + 1, col_idx + 1, f"se encontró '{char}' sin apertura")
                        top_char, top_line, top_col = stack.pop()
                        if top_char != pairs[char]:
                            return SyntaxResult(False, line_idx + 1, col_idx + 1, f"se encontró '{char}' pero se esperaba '{reverse_pairs[top_char]}' (abierto en línea {top_line})")
                            
                col_idx += 1
                
        if not stack.is_empty():
            top_char, top_line, top_col = stack.pop()
            return SyntaxResult(False, top_line, top_col, f"Apertura '{top_char}' sin cerrar")
            
        return SyntaxResult(True, 0, 0, "OK")

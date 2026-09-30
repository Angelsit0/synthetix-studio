"""Línea de comando separada en tokens. args[0] es el nombre del comando.

Soporta comillas:  insert 3 "    x = (1 + 2)"
"""
from __future__ import annotations


class CommandArgs:
    def __init__(self, raw: str, tokens: list, starts: list) -> None:
        self._raw = raw
        self._tokens = tokens
        self._starts = starts

    @staticmethod
    def parse(line: str) -> "CommandArgs":
        tokens, starts = [], []
        i, n = 0, len(line)
        while i < n:
            while i < n and line[i].isspace():
                i += 1
            if i >= n:
                break
            start = i
            token = ""
            if line[i] == '"':
                i += 1
                while i < n and line[i] != '"':
                    token += line[i]
                    i += 1
                i += 1
            else:
                while i < n and not line[i].isspace():
                    token += line[i]
                    i += 1
            tokens.append(token)
            starts.append(start)
        return CommandArgs(line, tokens, starts)

    @staticmethod
    def unescape(text: str) -> str:
        return text.replace("\\n", "\n").replace("\\t", "\t")

    def count(self) -> int:
        """Cantidad de tokens, incluyendo el nombre del comando."""
        return len(self._tokens)

    def is_empty(self) -> bool:
        return not self._tokens

    @property
    def name(self) -> str:
        return self._tokens[0]

    def __getitem__(self, index: int) -> str:
        return self._tokens[index]

    def rest(self, start_token: int) -> str:
        """Texto crudo desde el token indicado hasta el final (respeta espacios).
        Si todo el resto está entre comillas, se las quita."""
        if start_token >= len(self._tokens):
            return ""
        text = self._raw[self._starts[start_token]:].rstrip()
        if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
            text = text[1:-1]
        return text

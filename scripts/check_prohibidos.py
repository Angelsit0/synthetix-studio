"""Falla si en synthetix/ se usan estructuras u ordenamientos predefinidos
(el enunciado los prohíbe). Correr antes de cada commit; GitHub Actions también lo corre.

    python scripts/check_prohibidos.py
"""
import pathlib
import re
import sys

REGLAS = [
    (r"\.sort\(\s*(\)|key\s*=|reverse\s*=)", "método de ordenamiento de list"),
    (r"\bsorted\(", "función de ordenamiento integrada"),
    (r"\bcollections\b", "módulo collections (deque, OrderedDict...)"),
    (r"\bdeque\b", "deque"),
    (r"^\s*(import|from)\s+queue\b", "módulo queue (usa synthetix.ds.fifo_queue)"),
    (r"\bheapq\b", "heapq"),
    (r"\bbisect\b", "bisect"),
    (r"\bLifoQueue\b|\bSimpleQueue\b", "colas de la librería estándar"),
]

raiz = pathlib.Path(__file__).resolve().parent.parent / "synthetix"
errores = 0
for archivo in sorted(raiz.rglob("*.py")):
    for numero, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), start=1):
        for patron, que in REGLAS:
            if re.search(patron, linea):
                print(f"{archivo.relative_to(raiz.parent)}:{numero}: prohibido ({que}): {linea.strip()}")
                errores += 1

if errores:
    print(f"\nERROR: {errores} uso(s) prohibido(s). Usa las estructuras propias de synthetix/ds.")
    sys.exit(1)
print("OK: no se usan estructuras ni ordenamientos predefinidos.")

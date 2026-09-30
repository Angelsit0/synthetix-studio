"""Pruebas de Luis Orellana: Stack, History, SyntaxChecker, MergeSort y ShellSort.

    python -m unittest tests.test_luis -v
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from synthetix.analysis.diagnostic import Diagnostic, Severity  # noqa: E402
from synthetix.analysis.sorting import DiagnosticComparators, MergeSort, ShellSort  # noqa: E402
from synthetix.ds.stack import Stack  # noqa: E402
from synthetix.validation.history import History  # noqa: E402
from synthetix.validation.syntax_checker import SyntaxChecker  # noqa: E402


class TestStack(unittest.TestCase):
    def test_lifo(self):
        pila = Stack()
        pila.push(1)
        pila.push(2)
        self.assertEqual(len(pila), 2)
        self.assertEqual(pila.peek(), 2)
        self.assertEqual(pila.pop(), 2)
        self.assertEqual(pila.pop(), 1)
        self.assertTrue(pila.is_empty())

    def test_vacia(self):
        with self.assertRaises(IndexError):
            Stack().pop()
        with self.assertRaises(IndexError):
            Stack().peek()


class TestHistory(unittest.TestCase):
    def test_undo_redo(self):
        h = History()
        h.record("v1")  # el texto pasó de v1 a v2
        self.assertEqual(h.undo("v2"), "v1")
        self.assertEqual(h.redo("v1"), "v2")

    def test_nueva_edicion_vacia_redo(self):
        h = History()
        h.record("v1")
        h.undo("v2")
        self.assertTrue(h.can_redo())
        h.record("v1")
        self.assertFalse(h.can_redo())


class TestSyntaxChecker(unittest.TestCase):
    def test_balanceado(self):
        self.assertTrue(SyntaxChecker().check("def f(a):\n    return [a, {1: (2)}]\n").ok)

    def test_cierre_incorrecto(self):
        r = SyntaxChecker().check("x = (1 + 2]\n")
        self.assertFalse(r.ok)
        self.assertEqual((r.line, r.column), (1, 11))

    def test_cierre_sin_apertura(self):
        r = SyntaxChecker().check("a = 1\nb = 2)\n")
        self.assertFalse(r.ok)
        self.assertEqual((r.line, r.column), (2, 6))

    def test_sin_cerrar(self):
        r = SyntaxChecker().check("a = 1\nb = [1, 2\n")
        self.assertFalse(r.ok)
        self.assertEqual((r.line, r.column), (2, 5))

    def test_ignora_cadenas_y_comentarios(self):
        self.assertTrue(SyntaxChecker().check('print(")")  # (\n').ok)


def _al_azar(n):
    generador = random.Random(7)
    return [Diagnostic(generador.randint(1, 50), Severity(generador.randint(1, 3)), "r", str(i))
            for i in range(n)]


class TestOrdenamiento(unittest.TestCase):
    def _verificar(self, algoritmo):
        for n in (0, 1, 2, 17, 200):
            datos = _al_azar(n)
            esperado = sorted(datos, key=lambda d: (d.line, -d.severity))  # solo como referencia
            algoritmo.sort(datos, DiagnosticComparators.by_line_asc)
            self.assertEqual([(d.line, d.severity) for d in datos],
                             [(d.line, d.severity) for d in esperado])
        datos = _al_azar(50)
        algoritmo.sort(datos, DiagnosticComparators.by_severity_desc)
        self.assertEqual(datos[0].severity, Severity.ERROR)
        self.assertEqual(datos[-1].severity, Severity.INFO)

    def test_mergesort(self):
        self._verificar(MergeSort())

    def test_shellsort(self):
        self._verificar(ShellSort())

    def test_mergesort_es_estable(self):
        datos = [Diagnostic(5, Severity.WARNING, "r", "primero"),
                 Diagnostic(1, Severity.ERROR, "r", "x"),
                 Diagnostic(9, Severity.WARNING, "r", "segundo"),
                 Diagnostic(2, Severity.WARNING, "r", "tercero")]
        MergeSort().sort(datos, lambda a, b: a.severity > b.severity)
        self.assertEqual([d.message for d in datos], ["x", "primero", "segundo", "tercero"])


if __name__ == "__main__":
    unittest.main()

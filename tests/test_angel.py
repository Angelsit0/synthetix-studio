"""Pruebas de Angel Torres: LinkedList, FileManager y StaticAnalyzer.

    python -m unittest tests.test_angel -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from synthetix.analysis.diagnostic import Severity  # noqa: E402
from synthetix.analysis.static_analyzer import StaticAnalyzer  # noqa: E402
from synthetix.ds.linked_list import LinkedList  # noqa: E402
from synthetix.files.code_file import CodeFile  # noqa: E402
from synthetix.files.file_manager import FileManager  # noqa: E402


class TestLinkedList(unittest.TestCase):
    def test_insertar_recorrer_eliminar(self):
        lista = LinkedList()
        for valor in ("a", "b", "c"):
            lista.push_back(valor)
        self.assertEqual(len(lista), 3)
        self.assertEqual(list(lista), ["a", "b", "c"])
        self.assertTrue(lista.remove_at(1))
        self.assertEqual(list(lista), ["a", "c"])
        self.assertEqual(lista.at(1), "c")
        self.assertEqual(lista.index_of(lambda v: v == "c"), 1)
        self.assertEqual(lista.index_of(lambda v: v == "z"), -1)
        self.assertFalse(lista.remove_at(9))

    def test_eliminar_extremos(self):
        lista = LinkedList()
        for valor in (1, 2, 3):
            lista.push_back(valor)
        lista.remove_at(0)
        lista.remove_at(1)
        self.assertEqual(list(lista), [2])
        lista.push_back(4)
        self.assertEqual(list(lista), [2, 4])

    def test_clear(self):
        lista = LinkedList()
        lista.push_back(1)
        lista.clear()
        self.assertTrue(lista.is_empty())
        self.assertEqual(list(lista), [])


class TestFileManager(unittest.TestCase):
    def test_crear_buscar_cambiar(self):
        fm = FileManager()
        a = fm.create("a.py", "x = 1\n")
        b = fm.create("b.py", "y = 2\n")
        self.assertIs(fm.active, b)
        self.assertEqual(fm.count(), 2)
        self.assertIs(fm.find("a.py"), a)
        self.assertIs(fm.find(str(a.id)), a)
        self.assertIsNone(fm.find("nada.py"))
        self.assertTrue(fm.switch_to("a.py"))
        self.assertIs(fm.active, a)
        self.assertFalse(fm.switch_to("nada.py"))

    def test_nombre_repetido(self):
        fm = FileManager()
        fm.create("a.py", "")
        with self.assertRaises(ValueError):
            fm.create("a.py", "")

    def test_eliminar_activo(self):
        fm = FileManager()
        a = fm.create("a.py", "")
        fm.create("b.py", "")
        self.assertTrue(fm.remove("b.py"))
        self.assertIs(fm.active, a)
        self.assertEqual([f.name for f in fm], ["a.py"])
        self.assertTrue(fm.remove(str(a.id)))
        self.assertIsNone(fm.active)
        self.assertEqual(fm.count(), 0)
        self.assertFalse(fm.remove("a.py"))


class TestStaticAnalyzer(unittest.TestCase):
    def test_linea_muy_larga(self):
        archivo = CodeFile(1, "x.py", "a = 1\nb = '" + "x" * 120 + "'\n")
        diagnosticos = StaticAnalyzer(100, 40).analyze(archivo)
        self.assertTrue(any(d.line == 2 and d.severity == Severity.WARNING for d in diagnosticos))

    def test_codigo_limpio_sin_advertencias(self):
        archivo = CodeFile(1, "x.py", "def suma(a, b):\n    return a + b\n")
        diagnosticos = StaticAnalyzer(100, 40).analyze(archivo)
        self.assertFalse(any(d.severity >= Severity.WARNING for d in diagnosticos))


class TestLinkedListExtra(unittest.TestCase):
    """Casos de eliminación: único, primero, último y medio, revisando los enlaces."""

    @staticmethod
    def _lista(*valores):
        lista = LinkedList()
        for valor in valores:
            lista.push_back(valor)
        return lista

    def test_eliminar_unico_nodo(self):
        lista = self._lista("solo")
        nodo = lista._head
        self.assertTrue(lista.remove_at(0))
        self.assertTrue(lista.is_empty())
        self.assertIsNone(lista._head)
        self.assertIsNone(lista._tail)
        self.assertIsNone(nodo.prev)
        self.assertIsNone(nodo.next)
        with self.assertRaises(IndexError):
            lista.at(0)
        self.assertFalse(lista.remove_at(0))

    def test_eliminar_primero_ultimo_medio_desenlaza(self):
        lista = self._lista(1, 2, 3, 4, 5)
        primero = lista._head
        lista.remove_at(0)
        self.assertIsNone(primero.next)
        self.assertEqual(lista._head.value, 2)
        self.assertIsNone(lista._head.prev)

        ultimo = lista._tail
        lista.remove_at(len(lista) - 1)
        self.assertIsNone(ultimo.prev)
        self.assertEqual(lista._tail.value, 4)
        self.assertIsNone(lista._tail.next)

        medio = lista._head.next
        lista.remove_at(1)
        self.assertIsNone(medio.prev)
        self.assertIsNone(medio.next)
        self.assertEqual(list(lista), [2, 4])
        self.assertIs(lista._head.next, lista._tail)
        self.assertIs(lista._tail.prev, lista._head)

    def test_indices_negativos(self):
        lista = self._lista("a")
        self.assertFalse(lista.remove_at(-1))
        with self.assertRaises(IndexError):
            lista.at(-1)


class TestFileManagerExtra(unittest.TestCase):
    def test_eliminar_activo_pasa_al_siguiente(self):
        fm = FileManager()
        fm.create("a.py", "")
        b = fm.create("b.py", "")
        c = fm.create("c.py", "")
        fm.switch_to("b.py")
        self.assertTrue(fm.remove(str(b.id)))
        self.assertIs(fm.active, c)
        self.assertEqual([f.name for f in fm], ["a.py", "c.py"])

    def test_nombre_vacio(self):
        with self.assertRaises(ValueError):
            FileManager().create("   ", "")


class TestStaticAnalyzerReglas(unittest.TestCase):
    @staticmethod
    def _reglas(codigo, max_linea=100, max_funcion=40):
        archivo = CodeFile(1, "x.py", codigo)
        return [(d.line, d.rule) for d in StaticAnalyzer(max_linea, max_funcion).analyze(archivo)]

    def test_conteo_y_funcion_larga(self):
        codigo = "x = 1\ndef larga():\n    a = 1\n\n    b = 2\n    return a + b\ny = 2\n"
        reglas = self._reglas(codigo, max_funcion=3)
        self.assertIn((2, "function-lines"), reglas)
        self.assertIn((2, "function-too-long"), reglas)
        mensaje = StaticAnalyzer(100, 3).analyze(CodeFile(1, "x.py", codigo))[0].message
        self.assertIn("larga tiene 5 líneas", mensaje)

    def test_import_todo_espacios(self):
        codigo = "from os import *\nx = 1  # FIXME cambiar\ny = 2   \n"
        reglas = self._reglas(codigo)
        self.assertIn((1, "wildcard-import"), reglas)
        self.assertIn((2, "todo-comment"), reglas)
        self.assertIn((3, "trailing-whitespace"), reglas)
        self.assertEqual(len(reglas), 3)

    def test_anidamiento_un_aviso_por_bloque(self):
        profundo = " " * 20
        codigo = ("if a:\n" + profundo + "x = 1\n" + profundo + "y = 2\n"
                  + "\n" + profundo + "z = 3\n" + "b = 1\n" + profundo + "w = 4\n")
        lineas = [linea for linea, regla in self._reglas(codigo) if regla == "deep-nesting"]
        self.assertEqual(lineas, [2, 7])

    def test_archivo_con_errores_da_cinco_reglas(self):
        codigo = ("from math import *\n"
                  "def f(x):   \n"
                  "    if x:\n"
                  "        if x:\n"
                  "            if x:\n"
                  "                if x:\n"
                  "                    return 1  # TODO\n"
                  "    return '" + "z" * 120 + "'\n")
        reglas = set(regla for _, regla in self._reglas(codigo, max_funcion=3))
        self.assertGreaterEqual(len(reglas), 5)


if __name__ == "__main__":
    unittest.main()

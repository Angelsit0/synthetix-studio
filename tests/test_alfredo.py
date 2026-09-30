"""Pruebas de Alfredo Aureliano: Queue, HttpClient, AIClient y RequestBuffer.
No gastan cuota de la IA: usan respuestas simuladas.

    python -m unittest tests.test_alfredo -v
"""
import json
import os
import sys
import tempfile
import threading
import time
import unittest
import re

def strip_ansi(text: str) -> str:
    return re.sub(r'\033\[[0-9;]*m', '', text)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from synthetix.ai.ai_client import AIClient, AnalysisResult  # noqa: E402
from synthetix.ai.http_client import HttpClient, HttpResponse  # noqa: E402
from synthetix.ai.request_buffer import RequestBuffer  # noqa: E402
from synthetix.config.config import Config  # noqa: E402
from synthetix.ds.fifo_queue import Queue  # noqa: E402
from synthetix.util.logger import Logger  # noqa: E402


class TestQueue(unittest.TestCase):
    def test_fifo(self):
        cola = Queue()
        for valor in (1, 2, 3):
            cola.enqueue(valor)
        self.assertEqual(cola.front(), 1)
        self.assertEqual(cola.dequeue(), 1)
        self.assertEqual(list(cola), [2, 3])
        self.assertEqual(len(cola), 2)
        cola.dequeue()
        cola.dequeue()
        self.assertTrue(cola.is_empty())
        cola.enqueue(9)  # debe seguir funcionando después de vaciarse
        self.assertEqual(list(cola), [9])

    def test_vacia(self):
        with self.assertRaises(IndexError):
            Queue().dequeue()


class TestHttpClient(unittest.TestCase):
    def test_error_de_red_no_lanza_excepcion(self):
        respuesta = HttpClient().post_json("http://127.0.0.1:9/nada", "{}", {}, 3)
        self.assertFalse(respuesta.ok)
        self.assertTrue(respuesta.error)


def _config_de_prueba():
    datos = {"api": {"base_url": "http://127.0.0.1:9", "endpoint": "/chat/completions",
                     "model": "modelo-prueba", "api_key_env": "SYNTHETIX_CLAVE_QUE_NO_EXISTE",
                     "timeout_seconds": 3}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(datos, f)
    config = Config()
    config.load_from_file(f.name)
    os.unlink(f.name)
    return config


class TestAIClient(unittest.TestCase):
    def setUp(self):
        self.cliente = AIClient(_config_de_prueba(), HttpClient(), Logger())

    def test_cuerpo_de_la_peticion(self):
        cuerpo = json.loads(self.cliente._build_body("a.py", "print('hola')"))
        self.assertEqual(cuerpo["model"], "modelo-prueba")
        self.assertIn("print('hola')", json.dumps(cuerpo["messages"], ensure_ascii=False))

    def test_leer_respuesta_correcta(self):
        texto = "COMPLEJIDAD: O(n) en el peor caso\nREFACTORIZACION: usar una sola pasada"
        cuerpo = json.dumps({"choices": [{"message": {"content": texto}}]})
        resultado = self.cliente._parse_response(HttpResponse(status=200, body=cuerpo))
        self.assertTrue(resultado.ok)
        self.assertIn("O(n)", resultado.complexity)
        self.assertIn("una sola pasada", resultado.refactoring)

    def test_clave_invalida(self):
        resultado = self.cliente._parse_response(HttpResponse(status=401, body="{}"))
        self.assertFalse(resultado.ok)
        self.assertTrue(resultado.error)

    def test_sin_clave_no_llama_a_la_red(self):
        resultado = self.cliente.analyze("a.py", "x = 1")
        self.assertFalse(resultado.ok)
        self.assertTrue(resultado.error)


class _IAFalsa:
    """Reemplaza a AIClient: tarda un poco y anota el orden en que la llamaron."""

    def __init__(self):
        self.llamadas = []

    def analyze(self, file_name, code):
        self.llamadas.append(file_name)
        time.sleep(0.05)
        return AnalysisResult(ok=True, complexity="O(1)", refactoring="nada", raw="ok")


class TestRequestBuffer(unittest.TestCase):
    def test_despacha_en_orden_fifo(self):
        ia = _IAFalsa()
        buffer = RequestBuffer(ia, Logger())
        buffer.start()
        try:
            ids = [buffer.submit(f"archivo{i}.py", "x = 1") for i in range(3)]
            self.assertEqual(ids, [1, 2, 3])
            self.assertIsInstance(buffer.status_report(), str)
            limite = time.time() + 5
            while len(ia.llamadas) < 3 and time.time() < limite:
                time.sleep(0.02)
        finally:
            buffer.stop()
        self.assertEqual(ia.llamadas, ["archivo0.py", "archivo1.py", "archivo2.py"])
        self.assertIn("archivo2.py", buffer.results_report())


class TestQueueExtra(unittest.TestCase):
    def test_front_vacia_y_clear(self):
        cola = Queue()
        with self.assertRaises(IndexError):
            cola.front()
        for valor in ("a", "b"):
            cola.enqueue(valor)
        cola.clear()
        self.assertTrue(cola.is_empty())
        self.assertEqual(list(cola), [])
        cola.enqueue("c")
        self.assertEqual((cola.front(), len(cola)), ("c", 1))


class TestAIClientRespuestas(unittest.TestCase):
    def setUp(self):
        self.cliente = AIClient(_config_de_prueba(), HttpClient(), Logger())

    @staticmethod
    def _respuesta(texto):
        return HttpResponse(status=200, body=json.dumps({"choices": [{"message": {"content": texto}}]}))

    def test_limite_de_uso(self):
        resultado = self.cliente._parse_response(HttpResponse(status=429, body="{}"))
        self.assertFalse(resultado.ok)
        self.assertIn("429", resultado.error)

    def test_etiquetas_con_markdown_y_tilde(self):
        texto = "**COMPLEJIDAD:** O(n log n)\n\n**REFACTORIZACIÓN:**\n- extraer una función"
        resultado = self.cliente._parse_response(self._respuesta(texto))
        self.assertEqual(resultado.complexity, "O(n log n)")
        self.assertEqual(resultado.refactoring, "- extraer una función")

    def test_sin_etiquetas_no_pierde_la_respuesta(self):
        resultado = self.cliente._parse_response(self._respuesta("Todo es O(1)."))
        self.assertTrue(resultado.ok)
        self.assertIn("O(1)", resultado.complexity)


class _IABloqueada:
    """IA falsa que se queda 'pensando' hasta que la prueba la libera (sin depender de tiempos)."""

    def __init__(self):
        self.empezo = threading.Event()
        self.liberar = threading.Event()

    def analyze(self, file_name, code):
        self.empezo.set()
        self.liberar.wait(5)
        return AnalysisResult(ok=True, complexity="O(1)", refactoring="nada", raw="ok")


class _IAQueFalla:
    def __init__(self):
        self.llamadas = 0

    def analyze(self, file_name, code):
        self.llamadas += 1
        if self.llamadas == 1:
            raise ValueError("explotó")
        return AnalysisResult(ok=True, complexity="O(n)", refactoring="nada", raw="ok")


class TestRequestBufferExtra(unittest.TestCase):
    def test_estado_uno_en_proceso_y_pendientes_en_orden(self):
        ia = _IABloqueada()
        buffer = RequestBuffer(ia, Logger())
        buffer.start()
        try:
            for nombre in ("a.py", "b.py", "c.py"):
                buffer.submit(nombre, "x = 1")
            self.assertTrue(ia.empezo.wait(5))
            estado = strip_ansi(buffer.status_report())
            self.assertIn("En proceso: #1 a.py", estado)
            self.assertIn("1. #2 b.py", estado)
            self.assertIn("2. #3 c.py", estado)
            self.assertLess(estado.index("#2 b.py"), estado.index("#3 c.py"))
        finally:
            ia.liberar.set()
            buffer.stop()

    def test_stop_no_se_cuelga(self):
        buffer = RequestBuffer(_IAFalsa(), Logger())
        buffer.start()
        inicio = time.time()
        buffer.stop()
        self.assertLess(time.time() - inicio, 2)
        with self.assertRaises(RuntimeError):
            buffer.submit("a.py", "x = 1")

    def test_una_excepcion_no_mata_al_hilo(self):
        ia = _IAQueFalla()
        buffer = RequestBuffer(ia, Logger())
        buffer.start()
        try:
            buffer.submit("malo.py", "x = 1")
            buffer.submit("bueno.py", "x = 1")
            limite = time.time() + 5
            while "Respuestas sin ver: 2" not in strip_ansi(buffer.status_report()) and time.time() < limite:
                time.sleep(0.02)
        finally:
            buffer.stop()
        reporte = strip_ansi(buffer.results_report())
        self.assertIn("Error: fallo inesperado: explotó", reporte)
        self.assertIn("COMPLEJIDAD:\n  O(n)", reporte)
        self.assertNotIn("[error]", reporte)


if __name__ == "__main__":
    unittest.main()

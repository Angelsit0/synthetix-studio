"""Verificación completa de Synthetix Studio. Úsalo cuando quieras saber cómo va el proyecto:

    python scripts/verificar.py              # estado general (no falla por lo que aún falta)
    python scripts/verificar.py --estricto   # entrega final: todo implementado y en verde
    python scripts/verificar.py --probar-ia  # además hace UNA llamada real a la IA (gasta cuota)

Revisa, en este orden:
  1. Versión de Python
  2. config.json válido y con todas las claves que pide el enunciado
  3. Que todos los módulos importen sin errores (conectados entre sí)
  4. Que no se usen estructuras u ordenamientos prohibidos
  5. Que la prueba de humo (tests/smoke.txt) recorra todos los comandos sin caerse
  6. Las pruebas unitarias de cada integrante
  7. Los métodos que siguen sin implementar, por integrante
"""
from __future__ import annotations

import argparse
import importlib
import os
import pathlib
import pkgutil
import subprocess
import sys
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

INTEGRANTES = {
    "Angel Torres": {
        "pruebas": "test_angel",
        "archivos": ["synthetix/ds/linked_list.py", "synthetix/files/", "synthetix/config/",
                     "synthetix/analysis/static_analyzer.py", "synthetix/commands/file_commands.py",
                     "synthetix/commands/core_commands.py"],
    },
    "Luis Orellana": {
        "pruebas": "test_luis",
        "archivos": ["synthetix/ds/stack.py", "synthetix/validation/", "synthetix/analysis/sorting.py",
                     "synthetix/commands/validation_commands.py",
                     "synthetix/commands/analysis_commands.py"],
    },
    "Alfredo Aureliano": {
        "pruebas": "test_alfredo",
        "archivos": ["synthetix/ds/fifo_queue.py", "synthetix/ai/", "synthetix/commands/ai_commands.py"],
    },
}

CLAVES_CONFIG = ["paths.backups", "paths.logs", "api.base_url", "api.endpoint", "api.model",
                 "api.api_key_env"]

OK, FALTA, ERROR = "[ OK  ]", "[FALTA]", "[ERROR]"


class Verificador:
    def __init__(self, estricto: bool, probar_ia: bool) -> None:
        self.estricto = estricto
        self.probar_ia = probar_ia
        self.errores_graves: list = []
        self.pendientes_totales = 0
        self.pruebas_fallidas = 0

    # ------------------------------------------------------------------ utilidades
    @staticmethod
    def titulo(texto: str) -> None:
        print(f"\n=== {texto} ===")

    def grave(self, mensaje: str) -> None:
        self.errores_graves.append(mensaje)
        print(f"{ERROR} {mensaje}")

    @staticmethod
    def dueno_de(ruta: str) -> str:
        ruta = ruta.replace("\\", "/")
        for nombre, datos in INTEGRANTES.items():
            if any(ruta.startswith(prefijo) for prefijo in datos["archivos"]):
                return nombre
        return "Base (ya hecho)"

    # ------------------------------------------------------------------ pasos
    def python(self) -> None:
        self.titulo("1. Python")
        version = sys.version_info
        if version >= (3, 10):
            print(f"{OK} Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.grave(f"Python {version.major}.{version.minor}: se necesita 3.10 o superior")

    def configuracion(self) -> None:
        self.titulo("2. Archivo de configuración")
        from synthetix.config.config import Config, ConfigError
        config = Config()
        try:
            config.load_from_file(str(RAIZ / "config.json"))
        except ConfigError as e:
            self.grave(f"config.json: {e}")
            return
        faltan = [clave for clave in CLAVES_CONFIG if config.get(clave) in (None, "")]
        if faltan:
            self.grave("config.json no tiene: " + ", ".join(faltan))
        else:
            print(f"{OK} config.json válido (rutas de respaldos/logs y endpoint de la IA)")
        if config.api_key:
            print(f"{OK} Clave de la IA encontrada en ${config.get('api.api_key_env')}")
        else:
            print(f"{FALTA} Variable de entorno {config.get('api.api_key_env')} sin definir "
                  "(solo hace falta para usar 'analyze' de verdad)")

    def importaciones(self) -> None:
        self.titulo("3. Conexión entre módulos (importaciones)")
        import synthetix
        fallos = 0
        for info in pkgutil.walk_packages(synthetix.__path__, "synthetix."):
            try:
                importlib.import_module(info.name)
            except Exception as e:  # noqa: BLE001
                fallos += 1
                self.grave(f"{info.name} no importa: {type(e).__name__}: {e}")
        if not fallos:
            print(f"{OK} Todos los módulos de synthetix/ se importan correctamente")

    def prohibidos(self) -> None:
        self.titulo("4. Estructuras y ordenamientos prohibidos")
        proceso = subprocess.run([sys.executable, str(RAIZ / "scripts" / "check_prohibidos.py")],
                                 capture_output=True, text=True, encoding="utf-8", cwd=RAIZ)
        if proceso.returncode == 0:
            print(f"{OK} No se usa nada prohibido")
        else:
            print(proceso.stdout.strip())
            self.grave("Se usan estructuras u ordenamientos prohibidos (ver arriba)")

    def prueba_de_humo(self) -> None:
        self.titulo("5. Prueba de humo (todos los comandos de la consola)")
        entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
        entrada = (RAIZ / "tests" / "smoke.txt").read_text(encoding="utf-8")
        try:
            proceso = subprocess.run([sys.executable, "main.py", "config.json"], input=entrada,
                                     capture_output=True, text=True, encoding="utf-8",
                                     cwd=RAIZ, env=entorno, timeout=60)
        except subprocess.TimeoutExpired:
            self.grave("La consola se quedó colgada más de 60 s (¿un hilo que no termina?)")
            return
        salida = proceso.stdout + proceso.stderr
        if proceso.returncode != 0 or "Traceback" in salida:
            print(salida[-1500:])
            self.grave("La consola se cayó durante la prueba de humo (ver arriba)")
            return
        sin_implementar = salida.count("[sin implementar]")
        errores = salida.count("[error]") - sin_implementar
        print(f"{OK} La consola recorrió tests/smoke.txt completo sin caerse")
        if sin_implementar:
            print(f"{FALTA} {sin_implementar} comandos respondieron '[sin implementar]'")
        if errores > 0:
            print(f"{FALTA} {errores} comandos mostraron [error] "
                  "(revisar con: python main.py config.json < tests/smoke.txt)")
            self.pruebas_fallidas += errores

    def pruebas_unitarias(self) -> dict:
        self.titulo("6. Pruebas unitarias por integrante")

        class Registro(unittest.TestResult):
            def __init__(self) -> None:
                super().__init__()
                self.exitos: list = []

            def addSuccess(self, test) -> None:  # noqa: N802 (nombre de unittest)
                super().addSuccess(test)
                self.exitos.append(test)

        suite = unittest.defaultTestLoader.discover(str(RAIZ / "tests"), pattern="test_*.py",
                                                    top_level_dir=str(RAIZ / "tests"))
        registro = Registro()
        suite.run(registro)

        resumen = {nombre: {"ok": 0, "pendiente": 0, "falla": [], "total": 0}
                   for nombre in INTEGRANTES}

        def integrante(test) -> str:
            identificador = test.id()
            for nombre, datos in INTEGRANTES.items():
                if datos["pruebas"] in identificador:
                    return nombre
            return ""

        for test in registro.exitos:
            nombre = integrante(test)
            if nombre:
                resumen[nombre]["ok"] += 1
                resumen[nombre]["total"] += 1
        for test, traza in registro.failures + registro.errors:
            nombre = integrante(test)
            if not nombre:
                self.grave(f"Prueba sin dueño o con error de importación: {test.id()}")
                continue
            resumen[nombre]["total"] += 1
            if "[sin implementar]" in traza:
                resumen[nombre]["pendiente"] += 1
            else:
                ultima = traza.strip().splitlines()[-1]
                resumen[nombre]["falla"].append(f"{test.id().split('.', 1)[-1]} -> {ultima}")

        for nombre, datos in resumen.items():
            estado = OK if datos["ok"] == datos["total"] and datos["total"] else FALTA
            print(f"{estado} {nombre:<18} {datos['ok']}/{datos['total']} pruebas pasan"
                  + (f", {datos['pendiente']} esperan código sin implementar"
                     if datos["pendiente"] else ""))
            for falla in datos["falla"]:
                print(f"          falla: {falla}")
            self.pruebas_fallidas += len(datos["falla"]) + datos["pendiente"]
        return resumen

    def pendientes(self) -> None:
        self.titulo("7. Métodos sin implementar")
        conteo = {nombre: [] for nombre in INTEGRANTES}
        for archivo in sorted((RAIZ / "synthetix").rglob("*.py")):
            relativo = archivo.relative_to(RAIZ).as_posix()
            for linea in archivo.read_text(encoding="utf-8").splitlines():
                if "[sin implementar]" in linea and "raise" in linea:
                    metodo = linea.split("[sin implementar]")[1].strip(" \")'")
                    conteo.setdefault(self.dueno_de(relativo), []).append(metodo)
        for nombre, metodos in conteo.items():
            self.pendientes_totales += len(metodos)
            if metodos:
                print(f"{FALTA} {nombre:<18} {len(metodos)}: {', '.join(metodos)}")
            else:
                print(f"{OK} {nombre:<18} nada pendiente")

    def llamada_real_ia(self) -> None:
        self.titulo("8. Llamada real a la IA")
        from synthetix.ai.ai_client import AIClient
        from synthetix.ai.http_client import HttpClient
        from synthetix.config.config import Config
        from synthetix.util.logger import Logger
        config = Config()
        config.load_from_file(str(RAIZ / "config.json"))
        try:
            resultado = AIClient(config, HttpClient(), Logger()).analyze(
                "prueba.py", "def total(n):\n    return sum(i for i in range(n))\n")
        except NotImplementedError as e:
            print(f"{FALTA} {e}")
            return
        if resultado.ok:
            print(f"{OK} La IA respondió. Complejidad: {resultado.complexity[:120]}")
        else:
            self.grave(f"La IA no respondió bien: {resultado.error}")

    # ------------------------------------------------------------------ resultado
    def ejecutar(self) -> int:
        print("Verificación de Synthetix Studio")
        self.python()
        self.configuracion()
        self.importaciones()
        self.prohibidos()
        self.prueba_de_humo()
        self.pruebas_unitarias()
        self.pendientes()
        if self.probar_ia:
            self.llamada_real_ia()

        self.titulo("Resultado")
        if self.errores_graves:
            print("HAY PROBLEMAS que rompen el proyecto. Arreglarlos antes de hacer push:")
            for error in self.errores_graves:
                print(f"  - {error}")
            return 1
        if self.pendientes_totales or self.pruebas_fallidas:
            print("La base está bien conectada y no se cae. Falta trabajo:")
            print(f"  - {self.pendientes_totales} métodos sin implementar")
            print(f"  - {self.pruebas_fallidas} pruebas o comandos que aún no pasan")
            if self.estricto:
                print("Modo --estricto: el proyecto NO está listo para entregar.")
                return 1
            return 0
        print("TODO LISTO: implementado, conectado y con todas las pruebas en verde.")
        return 0


if __name__ == "__main__":
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Verificación de Synthetix Studio")
    parser.add_argument("--estricto", action="store_true",
                        help="falla si queda algo pendiente (usar para la entrega)")
    parser.add_argument("--probar-ia", action="store_true",
                        help="hace una llamada real a la IA (necesita la clave)")
    argumentos = parser.parse_args()
    sys.exit(Verificador(argumentos.estricto, argumentos.probar_ia).ejecutar())

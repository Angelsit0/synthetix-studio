# Synthetix Studio — Instrucciones para agentes de IA

> Este archivo lo leen Claude Code (vía CLAUDE.md), OpenCode y Antigravity.
> Es la fuente de verdad del proyecto: si algo contradice este archivo, gana este archivo.

## Contexto
Mini IDE por **línea de comandos** en **Python 3.10+**, sin librerías externas.
Proyecto 1 de *Algoritmos y Estructuras II* (Universidad José Antonio Páez). Se evalúa:
estructuras de datos PROPIAS, algoritmos de ordenamiento PROPIOS, POO completa, patrón Command,
calidad de commits/ramas, README e informe. Los integrantes deben poder explicar cada línea en
la defensa: escribe código claro y comentado, sin trucos ni "one-liners".

## Reglas NO negociables
1. **Prohibido** (baja la nota): métodos o funciones de ordenamiento integrados de Python,
   `collections` (deque, etc.), el módulo `queue`, `heapq`, `bisect`.
   Pilas y colas se hacen con NODOS ENLAZADOS (`synthetix/ds`), nunca con una `list` y
   `append`/`pop` por debajo. `scripts/check_prohibidos.py` lo verifica y GitHub Actions falla si aparece.
2. La `list` de Python se permite solo como arreglo simple (p. ej. los diagnósticos que se ordenan
   o las líneas de un archivo). Los algoritmos de ordenamiento se escriben a mano con índices.
3. Solo librería estándar: `json`, `os`, `threading`, `urllib`, `dataclasses`, `abc`, `time`, `datetime`.
4. **Todo en POO**: clases con una responsabilidad clara. Nada de lógica suelta en `main.py`.
5. **Interfaz por comandos**, nunca menús numerados (el enunciado lo penaliza).
6. **No cambies firmas públicas de clases de OTRO módulo.** Si hace falta, se propone en un PR aparte.
7. **Solo toca los archivos de tu módulo** (tabla de abajo). Si necesitas algo de otro módulo,
   deja un comentario `# NECESITO(Nombre): ...` y avisa.
8. **Nunca subas API keys.** La clave se lee de la variable de entorno indicada en
   `config.json` → `api.api_key_env` (por defecto `SYNTHETIX_API_KEY`).
9. Los métodos pendientes lanzan `NotImplementedError("[sin implementar] Clase.metodo")`.
   Al implementarlos, reemplaza esa línea por el código real.

## Arquitectura
```
main.py                   → Application().run()
synthetix/
├── app.py                Application: carga config, registra módulos, lanza la consola
├── core/                 Command, CommandArgs, CommandRegistry, Console (Invoker), AppContext
├── commands/             <modulo>_commands.py: clases Command de cada módulo + CommandUtils
├── ds/                   LinkedList, Stack, Queue (fifo_queue.py) con nodos enlazados
├── util/                 Logger
├── config/               Config (lee config.json; claves con puntos "api.base_url")
├── files/                CodeFile, FileManager, BackupManager
├── validation/           SyntaxChecker, History (Undo/Redo)
├── analysis/             Diagnostic, StaticAnalyzer, sorting (SortStrategy, MergeSort, ShellSort)
└── ai/                   HttpClient (urllib), AIClient, RequestBuffer (cola FIFO + hilo trabajador)
tests/                    smoke.txt (prueba de humo) y test_angel/test_luis/test_alfredo.py
scripts/                  verificar.py (estado del proyecto) y check_prohibidos.py
```
Patrones usados (van al informe y a la defensa):
- **Command**: `Console` (Invoker) → `CommandRegistry` → `Command.execute()` → receptores
  (`FileManager`, `CodeFile`, `SyntaxChecker`, `SortStrategy`, `RequestBuffer`).
- **Memento**: `History` guarda fotos completas del texto en dos pilas (Undo / Redo).
- **Strategy + Factory**: `SortStrategy` con `MergeSort` / `ShellSort`, creadas por `SortStrategyFactory`.
- **Productor–consumidor**: `RequestBuffer` = cola FIFO protegida por Lock/Condition + UN hilo que despacha en orden.

Flujo de una edición: comando `insert` → `CodeFile.insert_line()` → `apply_edit()` →
`History.record(estado_anterior)` → el texto cambia. **Toda** modificación pasa por `apply_edit()`.

## Dueños por módulo
| Persona | Rama | Archivos |
|---|---|---|
| Angel Torres — Archivos, Config, Análisis, integración | `feature/archivos` | `ds/linked_list.py`, `files/*`, `config/*`, `analysis/static_analyzer.py`, `commands/file_commands.py`, `commands/core_commands.py`, `README.md` |
| Luis Orellana — Validación, Historial, Ordenamiento | `feature/validacion-ordenamiento` | `ds/stack.py`, `validation/*`, `analysis/sorting.py`, `commands/validation_commands.py`, `commands/analysis_commands.py` |
| Alfredo Aureliano — Cola FIFO, HTTP, IA | `feature/cola-ia` | `ds/fifo_queue.py`, `ai/*`, `commands/ai_commands.py` |
| Todos | — | su sección de `docs/INFORME_TECNICO.md` y su archivo `tests/test_<nombre>.py` |

## Cómo agregar un comando
1. Crea una clase que herede de `Command` en `synthetix/commands/<tu_modulo>_commands.py`
   con `name`, `usage`, `description`, `min_args` y `execute(self, args, ctx)`.
2. Regístrala en `<TuModulo>CommandModule.register_into()` del mismo archivo.
3. Agrégala a la tabla de comandos del `README.md` y, si aplica, a `tests/smoke.txt`.
No hace falta tocar `app.py` ni `console.py`.

## Convenciones de código
- PEP 8, 4 espacios, líneas de máximo 100 caracteres, type hints en métodos públicos.
- Clases `PascalCase`, métodos y variables `snake_case`, atributos privados con `_` al inicio.
- Identificadores en inglés; docstrings, comentarios y mensajes al usuario en español.
- Errores: lanzar `ValueError` / `RuntimeError` / `IndexError` con mensaje claro.
  `Console` los muestra como `[error] ...` y los registra en `logs/synthetix.log`.
- Cada método de una estructura de datos documenta su complejidad en el docstring: `O(1)`.
- "Liberar nodos" en Python = desenlazar (`prev`/`next` = None) para que no quede ninguna referencia.

## Checklist antes de dar una tarea por terminada
1. `python scripts/verificar.py` → sin `[ERROR]`, y en tu fila todas tus pruebas en `[ OK  ]`.
2. Tus pruebas: `python -m unittest tests.test_<tu_nombre> -v` (test_angel, test_luis, test_alfredo).
   Si agregas pruebas, van en TU archivo de pruebas. No modifiques las existentes para que pasen.
4. Commits pequeños con Conventional Commits en español:
   `feat(pila): implementar push y pop`, `fix(cola): desenlazar nodos en clear`,
   `docs(informe): complejidad de mergesort`, `test(pila): caso de pila vacía`.
5. **Nunca** hacer push directo a `main`. Trabajar en tu rama y abrir Pull Request.
6. Explica al humano, en 5–10 líneas, qué hiciste y por qué, para que lo pueda defender.

# Informe técnico — Synthetix Studio

> Cada integrante completa su sección. Las complejidades marcadas con (*) son las esperadas:
> confirmarlas con la implementación final.

## 1. Arquitectura general
- Diagrama de clases: ver README (sección Arquitectura).
- Patrón **Command** *(Angel)*: Invoker (`Console`), registro (`CommandRegistry`), comando
  (`Command` y subclases) y receptores. Por qué facilita agregar comandos sin tocar la consola.
- Patrón **Strategy** en el motor de ordenamiento *(Luis)*.
- Patrón **Memento** en Undo/Redo *(Luis)*.
- **Productor–consumidor** en el buffer de peticiones *(Alfredo)*.

## 2. Estructuras de datos propias

| Estructura | Operación | Complejidad | Justificación |
|---|---|---|---|
| `LinkedList` (Angel) | `push_back` | O(1) (*) | referencia `_tail` |
| `LinkedList` (Angel) | `remove_at`, `at`, `index_of` | O(n) (*) | recorrido desde `_head` |
| `Stack` (Luis) | `push`, `pop`, `peek` | O(1) (*) | se opera solo en el tope |
| `Queue` (Alfredo) | `enqueue`, `dequeue` | O(1) (*) | referencias `_front` y `_back` |

## 3. Algoritmos

| Algoritmo | Tiempo | Espacio extra | Estable | Dueño |
|---|---|---|---|---|
| `SyntaxChecker.check` | O(n) (*) | O(n) peor caso | — | Luis |
| Undo / Redo | O(L) por copiar el texto de tamaño L (*) | O(k·L) para k cambios | — | Luis |
| MergeSort | O(n log n) en todos los casos (*) | O(n) | Sí | Luis |
| ShellSort (Knuth) | O(n^1.5) peor caso (*) | O(1) | No | Luis |
| `StaticAnalyzer.analyze` | O(total de caracteres) (*) | O(d) diagnósticos | — | Angel |

Comparar MergeSort vs ShellSort con mediciones reales (`sort` imprime los microsegundos) *(Luis)*.

## 4. Configuración externa *(Angel)*
Formato de `config.json`, claves usadas, por qué la API key va en variable de entorno.

## 5. Integración con la IA *(Alfredo)*
Endpoint, formato de la petición, cómo se extrae Big O y refactorización, manejo de errores.
Por qué un solo hilo trabajador + cola FIFO evita saturar el cliente HTTP.

## 6. Pruebas
Salida final de `python scripts/verificar.py --estricto` y casos de `tests/smoke.txt` por módulo.

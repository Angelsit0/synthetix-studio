# Informe técnico — Synthetix Studio

> Cada integrante completa su sección. Las complejidades marcadas con (*) son las esperadas:
> confirmarlas con la implementación final.

## 1. Arquitectura general
- Diagrama de clases: ver README (sección Arquitectura).
- Patrón **Command** *(Angel)*: cada acción de la consola es un objeto con la misma interfaz.
  - **Command** (clase abstracta en `core/command.py`): define `name`, `usage`, `description`,
    `min_args` y el método abstracto `execute(args, ctx)`. Cada comando (`NewCommand`,
    `CheckCommand`, `SortCommand`, `AnalyzeCommand`...) es una subclase.
  - **Invoker** (`Console`): lee la línea, la separa en `CommandArgs`, busca el comando en el
    registro, valida la cantidad de argumentos y llama `execute()`. No sabe qué hace cada comando,
    y atrapa cualquier excepción para mostrarla como `[error] ...` y registrarla en el log: la
    consola nunca se cae.
  - **Registro** (`CommandRegistry`): guarda los comandos y rechaza nombres duplicados. Cada
    módulo registra los suyos con `<Modulo>CommandModule.register_into(registry)`.
  - **Receptores** (en `AppContext`): `FileManager`, `CodeFile`, `Config`, `StaticAnalyzer`,
    `SyntaxChecker`, `SortStrategy`, `RequestBuffer`. Son los objetos que hacen el trabajo real.
  - **Ventaja**: agregar un comando es crear una subclase y registrarla; no se toca `Console` ni
    `app.py` (principio abierto/cerrado). Además, cada integrante trabajó sus comandos en su
    propio archivo sin pisar a los demás.
- Patrón **Strategy** en el motor de ordenamiento *(Luis)*.
- Patrón **Memento** en Undo/Redo *(Luis)*.
- **Productor–consumidor** en el buffer de peticiones *(Alfredo)*.

## 2. Estructuras de datos propias

| Estructura | Operación | Complejidad | Justificación |
|---|---|---|---|
| `LinkedList` (Angel) | `push_back` | O(1) | se engancha detrás de `_tail`, sin recorrer |
| `LinkedList` (Angel) | `remove_at`, `at` | O(n) | buscar el nodo recorre desde `_head` o desde `_tail` (la mitad más cercana: n/2 pasos como máximo); el re-enlace en sí es O(1) |
| `LinkedList` (Angel) | `index_of`, `__iter__`, `clear` | O(n) | visitan cada nodo una vez; `clear` desenlaza (`prev`/`next` = None) cada uno |
| `LinkedList` (Angel) | `__len__`, `is_empty` | O(1) | contador `_size` |
| `FileManager` (Angel) | `create` | O(n) | recorre para rechazar nombres repetidos; la inserción es O(1) |
| `FileManager` (Angel) | `find`, `switch_to`, `remove` | O(n) | búsqueda por id o nombre con `index_of`; `remove` además usa `remove_at` |
| `Stack` (Luis) | `push`, `pop`, `peek` | O(1) | se opera solo en el tope |
| `Queue` (Alfredo) | `enqueue`, `dequeue` | O(1) (*) | referencias `_front` y `_back` |

## 3. Algoritmos

| Algoritmo | Tiempo | Espacio extra | Estable | Dueño |
|---|---|---|---|---|
| `SyntaxChecker.check` | O(n) | O(n) peor caso | — | Luis |
| Undo / Redo | O(L) por copiar el texto de tamaño L | O(k·L) para k cambios | — | Luis |
| MergeSort | O(n log n) en todos los casos | O(n) | Sí | Luis |
| ShellSort (Knuth) | O(n^1.5) peor caso | O(1) | No | Luis |
| `StaticAnalyzer.analyze` | O(C), C = total de caracteres; O(p·C) con funciones anidadas a profundidad p | O(d) diagnósticos | — | Angel |



### 3.1 Lista de archivos *(Angel)*
`FileManager` guarda los archivos abiertos en la `LinkedList` propia (doblemente enlazada).
Se eligió doble y no simple porque cada nodo conoce a su anterior: al eliminar se re-enlazan
los vecinos directamente, y con `_tail` se inserta al final en O(1). Al eliminar se cubren
cuatro casos (único, primero, último y medio) actualizando `_head`/`_tail` cuando corresponde,
y el nodo se "libera" poniendo `prev`, `next` y `value` en `None`: sin referencias, el
recolector de basura de Python lo elimina. Si se borra el archivo activo, el nuevo activo es el
siguiente, si no el anterior, o ninguno si la lista queda vacía; se calcula **antes** de borrar.

### 3.2 Análisis estático *(Angel)*
`StaticAnalyzer.analyze` recorre el archivo una sola vez y devuelve los diagnósticos en orden de
aparición, **sin ordenar**: ordenarlos es trabajo de `sort` (MergeSort / ShellSort).

| Gravedad | Regla | Qué detecta |
|---|---|---|
| ERROR | `unbalanced-delimiters` | desbalance de `()`, `{}`, `[]` (reutiliza `SyntaxChecker`) |
| WARNING | `function-too-long` | función con más de `editor.max_function_lines` líneas |
| WARNING | `line-too-long` | línea con más de `editor.max_line_length` caracteres |
| WARNING | `wildcard-import` | `from modulo import *` |
| WARNING | `deep-nesting` | más de 4 niveles de indentación; un solo aviso por bloque |
| INFO | `function-lines` | conteo de líneas de cada función |
| INFO | `todo-comment` | comentarios con TODO o FIXME |
| INFO | `trailing-whitespace` | espacios o tabs al final de la línea |

El largo de una función va desde su `def` hasta la última línea no vacía con más indentación
que el `def`. Medirlo recorre el cuerpo de la función; con funciones anidadas ese cuerpo se
vuelve a recorrer por cada nivel, por eso el peor caso es O(p·C). Limitación conocida:
`todo-comment` toma el primer `#` de la línea, aunque esté dentro de una cadena.

### 3.3 Validaciones y Pila *(Luis)*
La estructura `Stack` se implementó mediante nodos enlazados, garantizando un acceso estricto de tipo LIFO (Last-In, First-Out). Las operaciones `push`, `pop` y `peek` se realizan en tiempo O(1) ya que solo se manipula la referencia al tope de la pila (`_top`).
`SyntaxChecker` utiliza la `Stack` para validar el balanceo de delimitadores `()`, `{}`, `[]`. Al iterar por cada caracter del código en O(n), los delimitadores de apertura se apilan con su línea y columna, y los de cierre se comparan con el tope, reportando desbalanceos exactos en O(n) de tiempo y O(n) de espacio en el peor caso. Ignora comentarios y strings.

### 3.4 Historial Undo/Redo (Patrón Memento) *(Luis)*
La clase `History` gestiona el historial de edición de cada archivo utilizando el patrón Memento apoyándose en dos instancias de `Stack` independientes (`_undo` y `_redo`).
- Antes de un cambio (`record`), el estado actual se apila en `_undo` y se vacía `_redo`.
- Al deshacer (`undo`), el estado pasa a `_redo` y se devuelve el tope de `_undo`. 
- Al rehacer (`redo`), el flujo es inverso. 
La complejidad temporal y espacial está directamente ligada al tamaño del texto guardado O(L).

### 3.5 Motor de Ordenamiento *(Luis)*
Se implementó el patrón Strategy para los algoritmos de ordenamiento de los diagnósticos estáticos en `sorting.py`. Los resultados obtenidos con 4 diagnósticos introducidos intencionalmente arrojaron los siguientes tiempos en la consola:

| Algoritmo | Tiempo | Memoria | Estable | Medición real |
|---|---|---|---|---|
| MergeSort | O(n log n) | O(n) extra | Sí | 8 µs |
| ShellSort | O(n^1.5) | O(1) in-place| No | 5 µs |

MergeSort es recursivo y mantiene el orden relativo original en diagnósticos con el mismo criterio evaluado (estable), ideal cuando importa dicho orden secundario. ShellSort utiliza la secuencia de Knuth (1, 4, 13, 40...) para optimizar las inserciones superando el O(n^2), ejecutándose in-place con complejidad espacial O(1).

## 4. Configuración externa *(Angel)*
Al iniciar, `Application` lee **obligatoriamente** el archivo indicado (`python main.py
config.json`); si no existe o el JSON es inválido, el programa termina con un mensaje claro.
El comando `config <ruta>` permite cargar otro durante la sesión; si falla, `Config` conserva la
configuración anterior. Las claves se consultan con puntos (`config.get("api.base_url")`).

| Clave | Uso |
|---|---|
| `paths.backups` | carpeta de respaldos automáticos (`save`, `delete` de un archivo modificado, `exit`) |
| `paths.logs` | carpeta del log de errores (`synthetix.log`) |
| `api.base_url` + `api.endpoint` | URL de la IA (formato OpenAI-compatible) |
| `api.model`, `api.timeout_seconds`, `api.max_tokens` | parámetros de conexión |
| `api.api_key_env` | **nombre** de la variable de entorno que tiene la clave |
| `editor.max_line_length`, `editor.max_function_lines` | límites del análisis estático |

**Por qué la API key va en una variable de entorno:** `config.json` se sube al repositorio, que
comparten los integrantes y el profesor; una clave escrita ahí quedaría pública en el historial
de Git aunque luego se borre, y cualquiera podría gastar la cuota. Por eso el archivo solo guarda
el nombre de la variable (`SYNTHETIX_API_KEY`) y cada persona define la clave en su propia PC.

## 5. Integración con la IA *(Alfredo)*
Endpoint, formato de la petición, cómo se extrae Big O y refactorización, manejo de errores.
Por qué un solo hilo trabajador + cola FIFO evita saturar el cliente HTTP.

## 6. Pruebas
Salida final de `python scripts/verificar.py --estricto` y casos de `tests/smoke.txt` por módulo.

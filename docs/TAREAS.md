# Plan de trabajo y reparto

El esqueleto ya corre: todos los comandos existen, las clases están definidas y cada método
pendiente muestra `[sin implementar]`. Cada persona trabaja en SUS archivos, en SU rama, con su
agente de IA, sin bloquear a nadie. Cada uno tiene su archivo de pruebas (`tests/test_angel.py`,
`tests/test_luis.py`, `tests/test_alfredo.py`): la meta es ponerlas en verde.
`python scripts/verificar.py` muestra en todo momento qué le falta a cada uno.

## Fases

| Fase | Quién | Qué | Listo cuando |
|---|---|---|---|
| 0. Arranque (1 h) | Angel | Crear repo, subir esqueleto a `main`, invitar a Luis, Alfredo y al profesor, proteger `main` | Los 3 clonan y ejecutan |
| 1. Módulos (paralelo) | Los 3 | Cada quien su checklist | Pasan sus pruebas y su parte de `smoke.txt` |
| 2. Integración | Los 3 | Merge de los 3 PRs, cambiar el CI a `verificar.py --estricto` | `verificar.py --estricto` dice TODO LISTO |
| 3. Entrega | Los 3 | README, informe técnico, ensayo de defensa | Cada uno explica TODOS los módulos |

Orden recomendado: Angel hace `LinkedList` + `FileManager` **primero** (los demás necesitan crear
archivos para probar en la consola). Mientras tanto Luis y Alfredo hacen su pila y su cola, que se
prueban solas con `unittest`.

---

## Angel Torres — Archivos, Config, Análisis estático, integración
Rama: `feature/archivos`

- [ ] `LinkedList` doble: `push_back`, `remove_at` (desenlazando el nodo), `at`, `index_of`, `__iter__`, `clear`
- [ ] `FileManager`: `create` (nombre repetido → error), `find` por id o nombre, `switch_to`, `remove`
- [ ] `StaticAnalyzer.analyze` con al menos 5 reglas (ver docstring), incluyendo conteo de líneas por función
- [ ] Revisar que `config.json` y el comando `config` cumplan el enunciado (rutas + endpoints)
- [ ] README: ejemplos de uso o capturas
- [ ] Informe: sección de LinkedList, FileManager, Config y StaticAnalyzer

**Prompt para tu agente:**
```
Lee AGENTS.md. Soy Angel Torres, rama feature/archivos. Implementa LinkedList en
synthetix/ds/linked_list.py como lista doblemente enlazada (_head/_tail), sin usar list ni
collections, respetando las firmas y documentando la complejidad de cada método. Haz que pasen
las pruebas TestLinkedList de tests/test_angel.py. Luego implementa FileManager
(synthetix/files/file_manager.py): find acepta id numérico o nombre; remove desenlaza el nodo;
si se borra el activo, el activo pasa al siguiente o al anterior. Corre la prueba de humo y haz
un commit por cada clase. No toques otros módulos. Al final explícame el código como si tuviera
que defenderlo ante el profesor.
```
Después, en otra sesión: *"Implementa StaticAnalyzer.analyze con las reglas del docstring y agrega pruebas en tests/..."*

---

## Luis Orellana — Pila, Validación, Undo/Redo, Ordenamiento
Rama: `feature/validacion-ordenamiento`

- [ ] `Stack` con nodos enlazados: `push`, `pop`, `peek` (`IndexError` si está vacía), `clear`
- [ ] `History`: `record`, `undo`, `redo` con las dos pilas
- [ ] `SyntaxChecker.check`: línea y columna del error; los 3 casos del docstring; ignorar delimitadores en cadenas y comentarios
- [ ] `MergeSort.sort` (estable) y `ShellSort.sort` (gaps de Knuth), sin métodos de ordenamiento integrados
- [ ] Probar `sort line mergesort`, `sort severity shellsort desc` con más de 20 diagnósticos
- [ ] Informe: Stack, SyntaxChecker, History, MergeSort vs ShellSort (complejidad y estabilidad)

**Prompt para tu agente:**
```
Lee AGENTS.md. Soy Luis Orellana, rama feature/validacion-ordenamiento. Implementa Stack en
synthetix/ds/stack.py con nodos enlazados (NO una list con append/pop). Luego History
(synthetix/validation/history.py) con las dos pilas, y SyntaxChecker.check reportando línea y
columna 1-based para: cierre sin apertura, cierre que no corresponde y apertura sin cerrar;
ignora delimitadores dentro de cadenas y comentarios. Haz que pasen TestStack, TestHistory y
TestSyntaxChecker de tests/test_luis.py. Commits pequeños. Al final explícame el algoritmo paso a paso con un ejemplo.
```
Después: *"Implementa MergeSort (estable) y ShellSort (gaps de Knuth) en synthetix/analysis/sorting.py y haz pasar TestOrdenamiento."*

---

## Alfredo Aureliano — Cola FIFO, HTTP, IA
Rama: `feature/cola-ia`

- [ ] `Queue` con nodos enlazados (`_front`, `_back`): `enqueue`, `dequeue`, `front`, `__iter__`, `clear`
- [ ] `HttpClient.post_json` con `urllib.request` (timeout, códigos HTTP, errores de red sin lanzar excepciones)
- [ ] `AIClient`: armar el JSON con `json.dumps`, enviar, extraer COMPLEJIDAD / REFACTORIZACION, manejar 401 y 429
- [ ] `RequestBuffer`: hilo trabajador único, `submit`, `status_report`, `results_report`, `stop` limpio
- [ ] Probar: 3 `analyze` seguidos → `queue-status` muestra 1 en proceso + 2 pendientes en orden
- [ ] Informe: Queue, productor-consumidor, por qué un solo hilo evita saturar el cliente HTTP

**Prompt para tu agente:**
```
Lee AGENTS.md. Soy Alfredo Aureliano, rama feature/cola-ia. Implementa Queue en
synthetix/ds/fifo_queue.py con nodos enlazados (NO list, NO collections, NO módulo queue) y haz
pasar TestQueue de tests/test_alfredo.py. Luego HttpClient.post_json con urllib.request y AIClient para un endpoint
OpenAI-compatible (/chat/completions), leyendo URL, modelo y la variable de entorno de la clave
desde Config. El prompt al modelo debe pedir exactamente dos secciones: "COMPLEJIDAD:" y
"REFACTORIZACION:". Después implementa RequestBuffer como productor-consumidor con
threading.Condition: submit encola bajo lock y notifica; UN hilo trabajador despacha en orden
FIFO y NO mantiene el lock durante la llamada HTTP. Commits pequeños. Explícame la
sincronización como para defenderla.
```

---

## Flujo de Git (todos)
```bash
git clone <url-del-repo>
cd synthetix-studio
git checkout -b feature/<tu-modulo>
# ...trabajar con el agente...
git add -A
git commit -m "feat(pila): implementar push y pop"
git push -u origin feature/<tu-modulo>
# Abrir Pull Request hacia main. Otro integrante lo revisa y aprueba.
```
- Traer lo último de `main` a tu rama seguido: `git pull origin main`.
- Commits pequeños y frecuentes (se evalúa la frecuencia y claridad).
- Revisión cruzada: Luis revisa a Angel, Alfredo revisa a Luis, Angel revisa a Alfredo.

## Para la defensa (4 pts)
- Cada integrante explica su módulo y al menos una pieza de otro módulo.
- Demo con `tests/smoke.txt` y un archivo con errores a propósito.
- Tener claras las complejidades de `docs/INFORME_TECNICO.md` sin leerlas.
- Evitar "códigos iguales": no copiar código de otros grupos; personalizar mensajes, reglas del
  analizador y nombres. Si el agente genera algo, entenderlo y adaptarlo.

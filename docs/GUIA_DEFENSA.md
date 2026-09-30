# Guía de Defensa — Synthetix Studio

> Esta guía es para los 3 integrantes. Léanla completa antes de la defensa.
> Cada uno debe poder explicar SU módulo en detalle y al menos entender los otros dos.

---

## ¿Qué es Synthetix Studio?

Imaginen un mini Visual Studio Code, pero que funciona **solo con texto en la terminal** (sin ventanas ni botones). Es un editor de código donde:

1. **Creas archivos** y los editas escribiendo comandos (`new`, `write`, `show`, etc.)
2. **Validas el código** — revisa si olvidaste cerrar un paréntesis (`check`)
3. **Deshaces y rehaces** cambios como Ctrl+Z / Ctrl+Y (`undo`, `redo`)
4. **Analizas la calidad** del código — te dice si hay líneas muy largas, funciones muy complicadas, etc. (`lint`)
5. **Ordenas los problemas** encontrados por línea o por gravedad (`sort`)
6. **Le pides a una IA** que analice la complejidad del código y sugiera mejoras (`analyze`)

Todo esto está construido con **estructuras de datos propias** (no usamos las que Python trae): listas enlazadas, pilas y colas hechas con nodos.

---

## ¿Cómo se divide el trabajo?

| Integrante | ¿Qué hizo? | Analogía simple |
|---|---|---|
| **Angel Torres** | Los archivos, la configuración y el análisis estático | Es como el "sistema de archivos" del editor: crea, guarda, lista y borra archivos. También es el "inspector de calidad" que revisa reglas del código |
| **Luis Orellana** | La validación de paréntesis, el historial y el ordenamiento | Es como el "corrector" que detecta errores de paréntesis, el Ctrl+Z/Ctrl+Y, y el organizador que ordena los problemas encontrados |
| **Alfredo Aureliano** | La cola de peticiones y la conexión con la IA | Es como un "asistente que hace fila": cuando le pides un análisis, no te hace esperar — lo pone en una cola y te avisa cuando termina |

---

## Parte de Angel Torres — Archivos y Análisis

### Lista enlazada (LinkedList)

**¿Qué es?** Una cadena de "cajas" donde cada caja tiene un archivo. Cada caja conoce a la siguiente y a la anterior (por eso es "doblemente enlazada").

```
[archivo1] ←→ [archivo2] ←→ [archivo3]
   ↑                            ↑
  HEAD                         TAIL
```

**¿Por qué doble y no simple?** Porque si quiero borrar un archivo del medio, necesito reconectar la caja anterior con la siguiente. Si fuera simple (solo flechas hacia adelante), tendría que recorrer toda la cadena para encontrar al anterior.

**¿Cómo se borra?** Se "desenganchan" los punteros:
- Si borro archivo2: archivo1 ahora apunta a archivo3, y archivo3 apunta a archivo1
- La caja de archivo2 queda suelta y Python la recoge automáticamente (garbage collector)

### FileManager (Gestor de archivos)

Usa la LinkedList para guardar todos los archivos abiertos. Siempre hay uno "activo" (el que estás editando).

- `new main.py` → crea una caja nueva al final de la cadena
- `list` → recorre toda la cadena mostrando cada archivo
- `switch` → cambia cuál es el archivo activo
- `delete` → desgancha la caja de la cadena

### StaticAnalyzer (Analizador estático)

Revisa el código **sin ejecutarlo** y encuentra problemas:
- `from math import *` → "no importes todo, importa solo lo que uses"
- Función con más de 40 líneas → "esa función es muy larga, divídela"
- 5 niveles de indentación → "tu código está muy anidado"
- `# TODO: revisar` → "tienes un pendiente"

**Demo:** `lint` muestra todos los problemas encontrados, sin ordenar. Ahí entra el trabajo de Luis.

### Patrón Command

Es la forma en que organizamos los comandos. Cada comando (como `new`, `delete`, `lint`) es un **objeto** independiente. La consola no sabe qué hace cada comando — solo busca el nombre y lo ejecuta. La ventaja: agregar un comando nuevo es crear una clase nueva, sin tocar nada más.

### Configuración (Config)

Lee `config.json` al iniciar. Ahí se guardan las rutas de respaldos, los límites del análisis y los datos de conexión con la IA. La clave de la IA **nunca** va en ese archivo (porque se sube a GitHub y cualquiera la vería).

---

## Parte de Luis Orellana — Validación, Historial y Ordenamiento

### Pila (Stack)

**¿Qué es?** Como una pila de platos: solo puedes poner o quitar platos de arriba.

```
     [plato3]  ← tope (el último que pusiste)
     [plato2]
     [plato1]
```

- `push` = poner un plato arriba → O(1), instantáneo
- `pop` = quitar el de arriba → O(1), instantáneo
- `peek` = mirar cuál está arriba sin quitarlo → O(1)

Está hecha con **nodos enlazados**, no con una lista de Python. Cada nodo apunta al siguiente.

### SyntaxChecker (Validador de sintaxis)

Usa la pila para verificar que cada `(` tenga su `)`, cada `{` su `}` y cada `[` su `]`.

**¿Cómo funciona?**
1. Recorre el código carácter por carácter
2. Si encuentra `(`, `{` o `[` → lo apila (con su línea y columna)
3. Si encuentra `)`, `}` o `]` → saca el tope de la pila y compara
   - Si coinciden → perfecto, sigue
   - Si no coinciden → error (ej: "cerraste con `)` pero abriste con `{` en la línea 3")
4. Al final, si la pila no está vacía → hay paréntesis sin cerrar

**Complejidad:** O(n) — recorre el código una sola vez.

**Demo:** `check` sobre código correcto dice "OK". Si insertas `roto = (a + b` (sin cerrar), `check` marca exactamente la línea y columna.

### History (Historial — Undo/Redo)

Usa **dos pilas**: una para Undo y otra para Redo.

```
UNDO:  [estado1, estado2, estado3]  ← tope
REDO:  [vacía]
```

- **Cuando editas**: se guarda una foto del texto en la pila Undo, y se vacía la pila Redo
- **Cuando haces Undo**: el estado actual va a Redo, y sacas el tope de Undo
- **Cuando haces Redo**: el estado actual va a Undo, y sacas el tope de Redo

**¿Por qué una edición nueva vacía Redo?** Porque si deshiciste 3 cambios y luego haces algo nuevo, ya no tiene sentido "rehacer" los cambios viejos — la línea temporal cambió.

### MergeSort y ShellSort

Dos algoritmos para ordenar los diagnósticos del `lint`.

**MergeSort** (divide y vencerás):
1. Divide la lista a la mitad
2. Ordena cada mitad (recursivamente)
3. Mezcla las dos mitades ordenadas
- Siempre O(n log n) — es predecible
- **Estable**: si dos diagnósticos tienen la misma gravedad, quedan en el orden original
- Usa O(n) de memoria extra (crea listas temporales)

**ShellSort** (inserción mejorada):
- Como ordenamiento por inserción, pero primero compara elementos lejanos y luego los va acercando
- Usa la secuencia de Knuth: gaps 1, 4, 13, 40...
- **No es estable**: puede cambiar el orden de elementos iguales
- Usa O(1) de memoria (ordena "en el lugar", sin crear listas nuevas)

**Demo:** `sort line mergesort` ordena los diagnósticos por línea. `sort severity shellsort desc` los ordena por gravedad de mayor a menor.

---

## Parte de Alfredo Aureliano — Cola de peticiones e IA

### Cola FIFO (Queue)

**¿Qué es?** Como la fila de un banco: el primero que llega es el primero que atienden.

```
FRENTE → [persona1] → [persona2] → [persona3] ← FONDO
         (la próxima    (espera)    (la última
          en ser                    que llegó)
          atendida)
```

- `enqueue` = ponerse en la fila (al fondo) → O(1)
- `dequeue` = atender al primero (sale del frente) → O(1)
- `front` = ver quién sigue sin sacarlo → O(1)

Hecha con nodos enlazados, con punteros `_front` y `_back`.

### HttpClient (Cliente HTTP)

Envía peticiones a la IA por internet (o en este caso, a Ollama que corre en tu propia máquina). Usa solo `urllib` (librería estándar de Python).

**Regla clave: nunca lanza excepciones.** Si algo falla (sin internet, clave incorrecta, timeout), devuelve el error como texto. Así el programa nunca se cae por un problema de red.

### AIClient (Cliente de IA)

Arma la pregunta para la IA y lee su respuesta:

1. **Arma el prompt**: le dice a la IA "eres un revisor de código, responde con COMPLEJIDAD: y REFACTORIZACION:"
2. **Envía el código** del archivo activo
3. **Lee la respuesta**: busca las etiquetas COMPLEJIDAD y REFACTORIZACION y separa las dos secciones
4. **Maneja errores**: si la clave es incorrecta (401), acceso denegado (403) o se acabó el límite (429), muestra un mensaje claro

### RequestBuffer (Buffer de peticiones — Productor-Consumidor)

Este es el corazón del módulo de Alfredo. Es un patrón llamado **productor-consumidor**:

**Productor** = la consola (tú):
- Cuando escribes `analyze`, se crea una solicitud y se mete en la cola
- La consola te devuelve el control inmediatamente — no esperas a que la IA responda

**Consumidor** = un hilo trabajador (en segundo plano):
- Es UN solo hilo que saca solicitudes de la cola de una en una
- Llama a la IA, espera la respuesta, y guarda el resultado
- Mientras trabaja, tú puedes seguir usando la consola normalmente

**¿Por qué un solo hilo?**
- Si mandáramos 10 peticiones a la vez, la IA nos bloquearía (error 429: "demasiadas peticiones")
- Con un solo hilo, las peticiones salen una por una, en orden FIFO

**¿Por qué se suelta el lock durante la llamada a la IA?**
- La IA tarda segundos en responder
- Si el hilo mantuviera el candado (lock), `queue-status` y `analyze` quedarían congelados
- Se suelta el lock solo mientras espera a la IA, y se vuelve a tomar para guardar el resultado

**¿Cómo cierra sin colgarse?**
- `exit` llama a `stop()`, que pone `_running = False`, despierta al hilo y espera a que termine
- Las peticiones que quedaban pendientes se descartan (se anotan en el log)

**Demo:**
```
analyze       → Solicitud #1 encolada
analyze       → Solicitud #2 encolada
analyze       → Solicitud #3 encolada
queue-status  → En proceso: #1, Pendientes: #2, #3
(esperar 30-60 segundos)
results       → Muestra Big O y refactorización de cada una
exit          → Cierra sin colgarse
```

---

## IA Local con Ollama

Usamos **Ollama**, que es una IA que corre en tu propia computadora:
- No necesita internet ni cuenta
- El modelo es `qwen2.5-coder:1.5b` (un modelo pequeño especializado en código)
- Se comunica igual que ChatGPT o Gemini (formato OpenAI-compatible)
- Se puede cambiar a un proveedor en la nube (Groq, Gemini, OpenRouter) solo editando `config.json`

**¿Por qué la clave de la IA va en una variable de entorno?**
Porque `config.json` se sube a GitHub. Si la clave estuviera ahí, cualquiera que vea el repositorio podría usarla y gastar nuestra cuota. Por eso solo se guarda el **nombre** de la variable (`SYNTHETIX_API_KEY`) y cada persona define la clave en su PC.

---

## Guion de la Demo (5 minutos)

> Practiquen esto los 3. Cualquiera debe poder hacerla.

### Paso 1 — Abrir (10 segundos)
```
python main.py config.json
help
```
**Decir:** "El programa lee la configuración al iniciar y muestra todos los comandos disponibles."

### Paso 2 — Crear y escribir un archivo (30 segundos)
```
new main.py
write
from math import *

def procesar(datos):   
    for d in datos:
        if d:
            while d:
                if d > 1:
                    d -= 1
                    print(d)
    # TODO: revisar
    return datos
.
show
```
**Decir:** "Creamos un archivo con `new`, escribimos código con `write`, y `show` lo muestra con números de línea. Los archivos se guardan en una **lista doblemente enlazada**."

### Paso 3 — Validar paréntesis (30 segundos)
```
check
insert 5 "    roto = (a + b"
check
```
**Decir:** "`check` usa una **pila** para verificar que cada paréntesis, llave y corchete tenga su par. Insertamos una línea con un paréntesis sin cerrar y `check` marca exactamente dónde está el error."

### Paso 4 — Undo/Redo (20 segundos)
```
undo
check
redo
history
```
**Decir:** "Undo y Redo funcionan con **dos pilas** (patrón Memento). Al deshacer, el estado actual pasa a la pila Redo. `history` muestra cuántos estados hay en cada pila."

### Paso 5 — Análisis estático y ordenamiento (40 segundos)
```
lint
sort line mergesort
sort severity shellsort desc
```
**Decir:** "`lint` encuentra problemas en el código sin ejecutarlo. `sort` los ordena: con **MergeSort** (estable, O(n log n)) o **ShellSort** (in-place, O(n^1.5)). Los dos algoritmos están escritos a mano, sin usar `sort()` ni `sorted()` de Python."

### Paso 6 — IA (1 minuto)
```
analyze
analyze
queue-status
```
**Decir:** "`analyze` encola el código para que la IA lo revise. La **cola FIFO** con un **único hilo trabajador** despacha las peticiones de una en una, para no saturar el servicio. `queue-status` muestra cuál está en proceso y cuáles esperan."

Esperar unos 30 segundos, luego:
```
results
```
**Decir:** "La IA responde con la complejidad Big O de cada función y propuestas de refactorización. Todo esto pasa en segundo plano — la consola nunca se congela."

### Paso 7 — Archivos y cierre (30 segundos)
```
new util.py
list
switch main.py
delete util.py
list
exit
```
**Decir:** "Podemos tener varios archivos abiertos en la lista enlazada. `exit` detiene el hilo de la IA, respalda los archivos sin guardar y cierra limpiamente."

---

## Preguntas frecuentes del profesor (y cómo responderlas)

### 1. ¿Por qué la lista es doble y no simple?
**Respuesta:** "Porque al eliminar un nodo del medio necesitamos re-enlazar el anterior con el siguiente. Con una lista doble, cada nodo ya conoce a ambos vecinos. Con una lista simple tendríamos que recorrer desde el inicio para encontrar al anterior, lo que sería O(n) extra."

### 2. ¿Cómo detecta la pila un cierre que no corresponde?
**Respuesta:** "Cada vez que encontramos un delimitador de apertura, lo apilamos con su línea y columna. Cuando encontramos uno de cierre, sacamos el tope de la pila y comparamos. Si no coinciden — por ejemplo, abrimos con `(` pero cerramos con `}` — reportamos el error con las posiciones exactas."

### 3. ¿Por qué dos pilas para Undo/Redo?
**Respuesta:** "Una pila guarda los estados anteriores y otra los estados que se deshicieron. Al hacer Undo, el estado actual pasa a Redo y recuperamos el tope de Undo. Al hacer Redo es al revés. Y cuando hacemos una edición nueva, vaciamos Redo porque la línea temporal cambió."

### 4. ¿Por qué MergeSort es estable y ShellSort no?
**Respuesta:** "MergeSort es estable porque al mezclar dos mitades, si dos elementos son iguales, siempre toma primero el de la izquierda, manteniendo el orden original. ShellSort mueve elementos a distancias grandes, y al hacerlo puede cambiar el orden relativo de elementos iguales."

### 5. ¿Qué pasa si piden 3 análisis seguidos?
**Respuesta:** "Se encolan los 3 en la cola FIFO. Un único hilo trabajador los despacha de uno en uno, en orden. Mientras tanto, la consola sigue respondiendo porque `submit` no espera a la IA. `queue-status` muestra cuál está en proceso y cuáles esperan."

### 6. ¿Por qué el hilo suelta el lock durante la llamada HTTP?
**Respuesta:** "Porque la IA tarda segundos en responder. Si el hilo mantuviera el lock, cualquier comando como `queue-status` o `analyze` quedaría bloqueado hasta que la IA respondiera. El lock solo protege las estructuras compartidas (la cola y la lista de resultados), nunca la llamada a la red."

### 7. ¿Cómo se agrega un comando nuevo sin tocar la consola?
**Respuesta:** "Usamos el patrón Command. Cada comando es una clase que hereda de Command y se registra en el CommandRegistry. La consola solo busca el nombre del comando en el registro y lo ejecuta. Agregar un comando nuevo es crear una clase nueva y registrarla, sin modificar Console ni app.py."

### 8. ¿Por qué la clave de la IA no está en config.json?
**Respuesta:** "Porque config.json se sube a GitHub y todo el historial de Git es público para los colaboradores. Si la clave estuviera ahí, quedaría expuesta incluso si la borramos después. Por eso config.json solo guarda el nombre de la variable de entorno, y cada persona define la clave en su propia máquina."

---

## Tips para la defensa

1. **No lean de la pantalla.** Practiquen la demo al menos 2 veces antes.
2. **Cada uno explica lo suyo.** Cuando el profesor pregunte sobre la pila, Luis responde. Si pregunta sobre la cola, Alfredo responde.
3. **Usen las palabras correctas:** nodos, punteros, FIFO, LIFO, O(n), estable, lock, productor-consumidor.
4. **Si no saben algo, sean honestos.** "No estoy seguro, pero creo que..." es mejor que inventar.
5. **Tengan Ollama corriendo** antes de la defensa (`ollama serve` si no se inicia solo).
6. **Prueben la demo con la VPN apagada** (si usan VPN), para evitar sorpresas.

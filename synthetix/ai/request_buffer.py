"""Buffer FIFO de peticiones a la IA (productor-consumidor). DUEÑO: Alfredo Aureliano

- La consola (productor) encola con submit() y sigue respondiendo al usuario.
- UN solo hilo trabajador (consumidor) despacha las peticiones de una en una, en estricto
  orden de llegada, para no saturar el cliente HTTP.
- Todo acceso a _pending/_completed va protegido por self._lock (dentro de self._condition).
- Prohibido usar el módulo queue de la librería estándar: la cola es synthetix.ds.fifo_queue.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from synthetix.ai.ai_client import AIClient, AnalysisResult
from synthetix.ds.fifo_queue import Queue
from synthetix.ds.linked_list import LinkedList
from synthetix.util.logger import Logger


@dataclass
class AnalysisRequest:
    id: int
    file_name: str
    code: str          # copia del código al momento de encolar
    created_at: str


@dataclass
class CompletedRequest:
    id: int
    file_name: str
    result: AnalysisResult = field(default_factory=AnalysisResult)
    shown: bool = False


class RequestBuffer:
    def __init__(self, client: AIClient, logger: Logger) -> None:
        self._client = client
        self._logger = logger
        self._pending = Queue()
        self._completed = LinkedList()   # CompletedRequest en orden de llegada
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._worker: Optional[threading.Thread] = None
        self._running = False
        self._next_id = 1
        self._processing: Optional[AnalysisRequest] = None

    def start(self) -> None:
        """Lanza el ÚNICO hilo trabajador (daemon=True: no impide cerrar el programa)."""
        with self._condition:
            if self._running:
                return
            self._running = True
        self._worker = threading.Thread(target=self._worker_loop, name="synthetix-ia",
                                        daemon=True)
        self._worker.start()

    def stop(self) -> None:
        """Avisa al hilo, espera a que termine la petición en curso y hace join.

        Las peticiones que seguían pendientes se descartan (quedan anotadas en el log):
        así 'exit' no espera a que la IA responda toda la cola. Si hay una petición en
        curso, el join puede tardar hasta api.timeout_seconds.
        """
        with self._condition:
            if not self._running:
                return
            self._running = False
            discarded = len(self._pending)
            self._pending.clear()
            self._condition.notify_all()     # despierta al hilo si estaba esperando
        if discarded:
            self._logger.info(f"IA: cola detenida, {discarded} peticiones pendientes descartadas")
        if self._worker is not None:
            self._worker.join()
            self._worker = None

    def submit(self, file_name: str, code: str) -> int:
        """Encola bajo lock, notifica al hilo y devuelve el id de la solicitud. O(1).

        Es el PRODUCTOR: no espera a la IA, así la consola sigue respondiendo.
        """
        with self._condition:
            if not self._running:
                raise RuntimeError("La cola de peticiones a la IA no está activa")
            request = AnalysisRequest(self._next_id, file_name, code,
                                      datetime.now().strftime("%H:%M:%S"))
            self._next_id += 1
            self._pending.enqueue(request)
            self._condition.notify()         # hay trabajo: despertar al hilo trabajador
        self._logger.info(f"IA: solicitud #{request.id} encolada ({file_name})")
        return request.id

    def status_report(self) -> str:
        """Texto para queue-status: en proceso, pendientes en orden FIFO y completadas sin ver.
        O(p + c), con p = pendientes y c = completadas."""
        with self._condition:
            lines = ["\033[96mCola de peticiones a la IA (FIFO, un solo hilo despacha de una en una):\033[0m"]
            if self._processing is None:
                lines.append("  En proceso: \033[90mninguna\033[0m")
            else:
                lines.append(f"  En proceso: \033[93m{self._describe(self._processing)}\033[0m")
            if self._pending.is_empty():
                lines.append("  Pendientes: \033[90mninguna\033[0m")
            else:
                lines.append(f"  Pendientes (\033[93m{len(self._pending)}\033[0m), en orden de salida:")
                position = 1
                for request in self._pending:
                    lines.append(f"    {position}. \033[97m{self._describe(request)}\033[0m")
                    position += 1
            unseen = self._count_unseen()
            hint = "\033[90m  (usa 'results')\033[0m" if unseen else ""
            color = "\033[92m" if unseen else "\033[90m"
            lines.append(f"  Respuestas sin ver: {color}{unseen}\033[0m{hint}")
        return "\n".join(lines)

    def results_report(self) -> str:
        """Texto para results (marca como vistas las completadas). O(c)."""
        with self._condition:
            report = ""
            for done in self._completed:
                if done.shown:
                    continue
                done.shown = True
                if report:
                    report += "\n\n"
                report += self._format_result(done)
        if not report:
            return "No hay respuestas nuevas de la IA. Usa 'queue-status' para ver la cola."
        return report

    def _worker_loop(self) -> None:
        """CONSUMIDOR: espera trabajo, saca la primera petición y la despacha.

        El lock se SUELTA durante la llamada a la IA (que puede tardar segundos): mientras
        tanto submit y queue-status siguen funcionando. Solo este hilo llama a la IA, así
        que nunca hay dos peticiones HTTP a la vez.
        """
        while True:
            with self._condition:
                # while y no if: al despertar se vuelve a comprobar la condición.
                while self._running and self._pending.is_empty():
                    self._condition.wait()
                if not self._running:
                    return
                request = self._pending.dequeue()
                self._processing = request

            result = self._call_ai(request)          # sin el lock

            with self._condition:
                self._completed.push_back(CompletedRequest(request.id, request.file_name,
                                                           result))
                self._processing = None
            estado = "ok" if result.ok else "con error"
            self._logger.info(f"IA: solicitud #{request.id} terminada ({estado})")

    # ------------------------------------------------------------------ ayudas

    def _call_ai(self, request: AnalysisRequest) -> AnalysisResult:
        """Llama a la IA sin dejar que una excepción inesperada mate al hilo trabajador."""
        try:
            return self._client.analyze(request.file_name, request.code)
        except Exception as e:  # noqa: BLE001 - el hilo no debe morir nunca
            self._logger.error(f"IA: fallo inesperado en #{request.id}: {e}")
            return AnalysisResult(error=f"fallo inesperado: {e}")

    def _count_unseen(self) -> int:
        """Completadas que el usuario aún no vio con 'results'. Llamar con el lock tomado."""
        count = 0
        for done in self._completed:
            if not done.shown:
                count += 1
        return count

    @staticmethod
    def _describe(request: AnalysisRequest) -> str:
        return f"#{request.id} {request.file_name} (encolada a las {request.created_at})"

    @staticmethod
    def _format_result(done: CompletedRequest) -> str:
        """Bloque de texto de una respuesta. Los errores se muestran como 'Error:' y no
        como '[error]', que es la marca de fallo de un comando en la consola."""
        header = f"\033[96m=== Solicitud #{done.id}: {done.file_name} ===\033[0m"
        result = done.result
        if not result.ok:
            return f"{header}\n\033[91mError: {result.error}\033[0m"
        return (f"{header}\n\033[93mCOMPLEJIDAD:\033[0m\n{RequestBuffer._indent(result.complexity)}"
                f"\n\033[92mREFACTORIZACION:\033[0m\n{RequestBuffer._indent(result.refactoring)}")

    @staticmethod
    def _indent(text: str) -> str:
        """Sangra cada línea con dos espacios para que se lea como bloque."""
        indented = ""
        for line in text.split("\n"):
            indented += "  " + line + "\n"
        return indented.rstrip("\n")

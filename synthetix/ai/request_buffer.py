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
from typing import Optional

from synthetix.ai.ai_client import AIClient, AnalysisResult
from synthetix.ds.fifo_queue import Queue
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
        self._completed: list = []
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._worker: Optional[threading.Thread] = None
        self._running = False
        self._next_id = 1
        self._processing: Optional[AnalysisRequest] = None

    def start(self) -> None:
        """Lanza el hilo trabajador (daemon=True)."""
        # TODO(Alfredo): self._running = True
        #   self._worker = threading.Thread(target=self._worker_loop, daemon=True); start()
        pass

    def stop(self) -> None:
        """Avisa al hilo, espera a que termine la petición en curso y hace join."""
        # TODO(Alfredo): with self._condition: self._running = False; notify_all(); join()
        pass

    def submit(self, file_name: str, code: str) -> int:
        """Encola bajo lock, notifica al hilo y devuelve el id de la solicitud."""
        raise NotImplementedError("[sin implementar] RequestBuffer.submit")

    def status_report(self) -> str:
        """Texto para queue-status: en proceso, pendientes en orden FIFO y completadas sin ver."""
        raise NotImplementedError("[sin implementar] RequestBuffer.status_report")

    def results_report(self) -> str:
        """Texto para results (marca como vistas las completadas)."""
        raise NotImplementedError("[sin implementar] RequestBuffer.results_report")

    def _worker_loop(self) -> None:
        """while True: esperar con condition.wait() hasta que haya pendientes o se detenga;
        dequeue; SOLTAR el lock durante la llamada HTTP; volver a tomarlo y guardar el resultado."""
        raise NotImplementedError("[sin implementar] RequestBuffer._worker_loop")

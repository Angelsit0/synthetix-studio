"""Arma el prompt, llama al endpoint de config.json y separa la complejidad Big O
de las propuestas de refactorización.                       DUEÑO: Alfredo Aureliano

Formato del endpoint: OpenAI-compatible (/chat/completions). Sirve con Groq, Gemini
(endpoint OpenAI-compatible), OpenRouter u OpenAI cambiando solo config.json.
"""
from __future__ import annotations

from dataclasses import dataclass

from synthetix.ai.http_client import HttpClient, HttpResponse
from synthetix.config.config import Config
from synthetix.util.logger import Logger


@dataclass
class AnalysisResult:
    ok: bool = False
    complexity: str = ""    # ej: "Peor caso O(n^2) por el doble for en ordenar()"
    refactoring: str = ""   # propuestas de refactorización
    raw: str = ""           # texto completo que devolvió el modelo
    error: str = ""


class AIClient:
    def __init__(self, config: Config, http: HttpClient, logger: Logger) -> None:
        self._config = config
        self._http = http
        self._logger = logger

    def analyze(self, file_name: str, code: str) -> AnalysisResult:
        """Pistas:
        1. Si self._config.api_key está vacía -> AnalysisResult(error=...) sin llamar a la red.
        2. headers: {"Content-Type": "application/json", "Authorization": "Bearer <clave>"}
        3. self._http.post_json(self._config.api_url, self._build_body(...), headers, self._config.api_timeout)
        4. self._parse_response(...) y registrar errores con self._logger.error(...)
        """
        raise NotImplementedError("[sin implementar] AIClient.analyze")

    def _build_body(self, file_name: str, code: str) -> str:
        """json.dumps({"model": ..., "messages": [{"role": "system", ...}, {"role": "user", ...}]})
        Pedirle al modelo que responda EXACTAMENTE con dos secciones:
            COMPLEJIDAD: ...
            REFACTORIZACION: ...
        """
        raise NotImplementedError("[sin implementar] AIClient._build_body")

    def _parse_response(self, response: HttpResponse) -> AnalysisResult:
        """El texto viene en choices[0].message.content; separar por las etiquetas
        COMPLEJIDAD: y REFACTORIZACION:. Manejar 401 (clave inválida) y 429 (límite de uso)."""
        raise NotImplementedError("[sin implementar] AIClient._parse_response")

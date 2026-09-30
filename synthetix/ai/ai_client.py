"""Arma el prompt, llama al endpoint de config.json y separa la complejidad Big O
de las propuestas de refactorización.                       DUEÑO: Alfredo Aureliano

Formato del endpoint: OpenAI-compatible (/chat/completions). Sirve con Groq, Gemini
(endpoint OpenAI-compatible), OpenRouter u OpenAI cambiando solo config.json.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from synthetix.ai.http_client import HttpClient, HttpResponse
from synthetix.config.config import Config
from synthetix.util.logger import Logger

# Etiquetas que se le exigen al modelo. Al leerlas se ignoran mayúsculas y la tilde.
_COMPLEXITY_LABEL = "COMPLEJIDAD"
_REFACTORING_LABEL = "REFACTORIZACION"

_SYSTEM_PROMPT = (
    "Eres un revisor de código experto en análisis de algoritmos. Responde en español y "
    "EXACTAMENTE con dos secciones, en este orden y con estas etiquetas:\n"
    "COMPLEJIDAD: la complejidad temporal y espacial en notación Big O (peor caso) de cada "
    "función relevante, justificada en una o dos frases.\n"
    "REFACTORIZACION: propuestas concretas para mejorar el código (legibilidad, eficiencia, "
    "errores). Si no hay nada que mejorar, dilo.\n"
    "No agregues texto antes de COMPLEJIDAD ni otras secciones."
)


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
        """Envía el código a la IA y devuelve la complejidad y la refactorización.

        Sin clave no se llama a la red. Nunca lanza excepciones: los problemas vuelven
        en AnalysisResult.error y quedan registrados en el log.
        """
        api_key = self._config.api_key
        if not api_key:
            variable = self._config.get("api.api_key_env", "SYNTHETIX_API_KEY")
            return AnalysisResult(error=f"falta la clave de la IA: define la variable de "
                                        f"entorno {variable}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            # Agente propio: algunos proveedores rechazan el de urllib por defecto.
            "User-Agent": "SynthetixStudio/0.1",
        }
        response = self._http.post_json(self._config.api_url, self._build_body(file_name, code),
                                        headers, self._config.api_timeout)
        result = self._parse_response(response)
        if not result.ok:
            self._logger.error(f"IA ({file_name}): {result.error}")
        return result

    def _build_body(self, file_name: str, code: str) -> str:
        """Cuerpo JSON en formato OpenAI-compatible: modelo, límite de tokens y dos
        mensajes (las reglas de respuesta como 'system' y el código como 'user')."""
        body = {
            "model": self._config.api_model,
            "max_tokens": self._config.get_int("api.max_tokens", 1024),
            "temperature": 0.2,     # baja: respuestas estables y con el formato pedido
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",
                 "content": f"Analiza el archivo {file_name}:\n\n{code}"},
            ],
        }
        return json.dumps(body, ensure_ascii=False)

    def _parse_response(self, response: HttpResponse) -> AnalysisResult:
        """Traduce la respuesta HTTP a un AnalysisResult.

        Errores con mensaje claro: red, 401 (clave inválida), 403 (acceso denegado),
        429 (límite de uso) y cualquier otro código. Si todo va bien, el texto viene en
        choices[0].message.content y se separa en las secciones COMPLEJIDAD y REFACTORIZACION.
        """
        if response.error:
            return AnalysisResult(error=f"sin conexión con la IA: {response.error}")
        if response.status == 401:
            return AnalysisResult(error="clave inválida (401): revisa la variable de entorno "
                                        "de la clave")
        if response.status == 403:
            return AnalysisResult(error="acceso denegado (403): el proveedor bloquea esta red "
                                        "o la clave no tiene permiso")
        if response.status == 429:
            return AnalysisResult(error="límite de uso alcanzado (429): espera un minuto y "
                                        "vuelve a intentar")
        if not 200 <= response.status < 300:
            detail = self._api_error_message(response.body)
            return AnalysisResult(error=f"la IA respondió HTTP {response.status}: {detail}")

        try:
            data = json.loads(response.body)
            text = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError):
            return AnalysisResult(error="respuesta de la IA con formato inesperado")
        if not isinstance(text, str) or not text.strip():
            return AnalysisResult(error="la IA devolvió una respuesta vacía")

        complexity, refactoring = self._split_sections(text)
        if not complexity and not refactoring:
            # El modelo no usó las etiquetas: no se pierde la respuesta, va completa.
            return AnalysisResult(ok=True, complexity=text.strip(),
                                  refactoring="(el modelo no usó el formato pedido; "
                                              "ver la complejidad)", raw=text)
        return AnalysisResult(ok=True, complexity=complexity, refactoring=refactoring, raw=text)

    # ------------------------------------------------------------------ ayudas

    def _split_sections(self, text: str) -> tuple:
        """Recorre el texto línea por línea: cada línea va a la sección de la última
        etiqueta vista. Devuelve (complejidad, refactorización); vacíos si no hay etiquetas."""
        complexity = ""
        refactoring = ""
        section = ""
        for line in text.split("\n"):
            label, rest = self._split_label(line)
            if label:
                section = label
                line = rest
            if section == _COMPLEXITY_LABEL:
                complexity += line + "\n"
            elif section == _REFACTORING_LABEL:
                refactoring += line + "\n"
        return complexity.strip(), refactoring.strip()

    @staticmethod
    def _split_label(line: str) -> tuple:
        """Si la línea empieza con una etiqueta devuelve (etiqueta, resto); si no, ("", línea).

        Tolera lo que suelen agregar los modelos: markdown (**COMPLEJIDAD:**, ## ...),
        minúsculas y la tilde de REFACTORIZACIÓN.
        """
        clean = line.strip().lstrip("*# ")
        normalized = clean.upper().replace("Ó", "O")
        for label in (_COMPLEXITY_LABEL, _REFACTORING_LABEL):
            if normalized.startswith(label):
                rest = clean[len(label):].lstrip("*: ")
                return label, rest
        return "", line

    @staticmethod
    def _api_error_message(body: str) -> str:
        """Mensaje de error que manda el proveedor en {"error": {"message": ...}}."""
        try:
            return str(json.loads(body)["error"]["message"])
        except (ValueError, KeyError, TypeError):
            return body[:200] if body else "sin detalle"

"""Cliente HTTP (solo librería estándar: urllib).           DUEÑO: Alfredo Aureliano"""
from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class HttpResponse:
    status: int = 0     # código HTTP (200, 401, 429...)
    body: str = ""
    error: str = ""     # error de red; vacío si no hubo

    @property
    def ok(self) -> bool:
        return not self.error and 200 <= self.status < 300


class HttpClient:
    def post_json(self, url: str, body: str, headers: dict, timeout: int) -> HttpResponse:
        """Envía un POST con cuerpo JSON y devuelve la respuesta sin lanzar excepciones.

        - Respuesta 2xx: status y body.
        - Error HTTP (401, 429, 500...): urllib lo lanza como HTTPError; se devuelve su
          código y su cuerpo, para que AIClient decida qué mensaje mostrar.
        - Error de red (sin conexión, DNS, timeout) o URL mal escrita: se devuelve en error.
        """
        try:
            # Armar el Request va dentro del try: con una URL mal escrita ya lanza ValueError.
            request = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers,
                                             method="POST")
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return HttpResponse(status=response.status,
                                    body=response.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as e:
            # HTTPError es subclase de URLError: por eso se captura primero.
            return HttpResponse(status=e.code, body=self._read_error_body(e))
        except urllib.error.URLError as e:
            return HttpResponse(error=f"no se pudo conectar con {url}: {e.reason}")
        except TimeoutError:
            return HttpResponse(error=f"la IA no respondió en {timeout} segundos")
        except (OSError, ValueError) as e:
            # OSError: fallos de red de bajo nivel; ValueError: URL mal escrita en config.json.
            return HttpResponse(error=f"error de conexión: {e}")

    @staticmethod
    def _read_error_body(error: urllib.error.HTTPError) -> str:
        """Cuerpo de un error HTTP; vacío si tampoco se puede leer."""
        try:
            return error.read().decode("utf-8", errors="replace")
        except OSError:
            return ""

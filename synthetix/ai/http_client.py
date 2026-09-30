"""Cliente HTTP (solo librería estándar: urllib).           DUEÑO: Alfredo Aureliano"""
from __future__ import annotations

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

        Pistas: urllib.request.Request(url, data=body.encode("utf-8"), headers=headers,
        method="POST"); urllib.request.urlopen(req, timeout=timeout).
        Capturar urllib.error.HTTPError (tiene .code y .read()) y urllib.error.URLError.
        """
        raise NotImplementedError("[sin implementar] HttpClient.post_json")

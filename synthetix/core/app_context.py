"""Contexto compartido que reciben todos los comandos (los receptores del patrón Command)."""
from __future__ import annotations

from synthetix.ai.ai_client import AIClient
from synthetix.ai.http_client import HttpClient
from synthetix.ai.request_buffer import RequestBuffer
from synthetix.config.config import Config
from synthetix.files.file_manager import FileManager
from synthetix.util.logger import Logger


class AppContext:
    def __init__(self) -> None:
        self.config = Config()
        self.logger = Logger()
        self.files = FileManager()
        self.http = HttpClient()
        self.ai = AIClient(self.config, self.http, self.logger)
        self.requests = RequestBuffer(self.ai, self.logger)
        self.running = True

import abc
from dataclasses import dataclass

from fastapi import FastAPI

from stac_api.clients.base import BaseCoreClient


@dataclass
class StacBackend(abc.ABC):
    client: BaseCoreClient

    @abc.abstractmethod
    def register(self, app: FastAPI):
        """register backend with the application"""
        ...
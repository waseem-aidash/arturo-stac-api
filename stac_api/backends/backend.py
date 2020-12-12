import abc
from dataclasses import dataclass

from fastapi import FastAPI
from starlette.datastructures import State

from stac_api.clients.base import BaseCoreClient


@dataclass
class StacBackend(abc.ABC):
    client: BaseCoreClient
    state: State = State()

    def register(self, app: FastAPI):
        """register backend with the application"""

        # inject state
        self.state = app.state
        self.client.inject_state(app.state)


        # add event handlers
        if hasattr(self, "on_startup"):
            app.add_event_handler("startup", self.on_startup)

        if hasattr(self, "on_shutdown"):
            app.add_event_handler("startup", self.on_shutdown)


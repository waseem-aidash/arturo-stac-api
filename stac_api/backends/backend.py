from dataclasses import dataclass

from stac_api.clients.base import BaseCoreClient


@dataclass
class StacBackend:
    client: BaseCoreClient


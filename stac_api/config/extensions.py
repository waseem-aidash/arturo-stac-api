import abc
from dataclasses import dataclass, field
from typing import Set

from fastapi import FastAPI

from stac_api.clients.postgres.transactions import TransactionsClient


@dataclass
class ApiExtension(abc.ABC):
    """api extension base class"""

    @abc.abstractmethod
    def add_to_api(self, app: FastAPI):
        """add extension to api"""
        ...


@dataclass
class Context(ApiExtension):
    """context extension"""

    def add_to_api(self, app: FastAPI):
        """add extension to api"""
        raise NotImplementedError


@dataclass
class Fields(ApiExtension):
    """fields extension"""

    indexed_fields: Set[str]
    default_includes: Set[str] = field(
        default_factory=lambda: {
            "id",
            "type",
            "geometry",
            "bbox",
            "links",
            "assets",
            "properties.datetime",
        }
    )

    def add_to_api(self, app: FastAPI):
        """add extension to api"""

        raise NotImplementedError


@dataclass
class Query(ApiExtension):
    """query extension"""

    def add_to_api(self, app: FastAPI):
        """add extension to api"""

        raise NotImplementedError


class Sort(ApiExtension):
    """sort extension"""

    def add_to_api(self, app: FastAPI):
        """add extension to api"""

        raise NotImplementedError


class Transaction(ApiExtension):
    """transaction extension"""

    client: TransactionsClient = TransactionsClient()

    def add_to_api(self, app: FastAPI):
        """add extension to api"""

        raise NotImplementedError

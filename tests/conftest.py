import json
import os
from typing import Callable, Dict

import pytest
from starlette.testclient import TestClient

from stac_api.api.app import StacApi
from stac_api.api.extensions import (
    ContextExtension,
    FieldsExtension,
    QueryExtension,
    SortExtension,
    TransactionExtension,
)
from stac_api.clients.postgres.core import CoreCrudClient
from stac_api.clients.postgres.session import Session
from stac_api.clients.postgres.transactions import (
    BulkTransactionsClient,
    TransactionsClient,
)
from stac_api.config import PostgresSettings, inject_settings
from stac_api.models import database
from stac_api.models.schemas import Collection

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class TestSettings(PostgresSettings):
    class Config:
        env_file = ".env.test"


settings = TestSettings()
inject_settings(settings)


@pytest.fixture(autouse=True)
def cleanup(postgres_core: CoreCrudClient, postgres_transactions: TransactionsClient):
    yield
    collections = postgres_core.all_collections(request=MockStarletteRequest)
    for coll in collections:
        if coll.id.split("-")[0] == "test":
            # Delete the items
            items = postgres_core.item_collection(
                coll.id, limit=100, request=MockStarletteRequest
            )
            for feat in items.features:
                postgres_transactions.delete_item(feat.id, request=MockStarletteRequest)

            # Delete the collection
            postgres_transactions.delete_collection(
                coll.id, request=MockStarletteRequest
            )


@pytest.fixture
def load_test_data() -> Callable[[str], Dict]:
    def load_file(filename: str) -> Dict:
        with open(os.path.join(DATA_DIR, filename)) as file:
            return json.load(file)

    return load_file


class MockStarletteRequest:
    base_url = "http://test-server"


@pytest.fixture
def db_session() -> Session:
    return Session(
        reader_conn_string=settings.reader_connection_string,
        writer_conn_string=settings.writer_connection_string,
    )


@pytest.fixture
def postgres_core(db_session):
    return CoreCrudClient(
        session=db_session,
        item_table=database.Item,
        collection_table=database.Collection,
        token_table=database.PaginationToken,
    )


@pytest.fixture
def postgres_transactions(db_session):
    return TransactionsClient(
        session=db_session,
        item_table=database.Item,
        collection_table=database.Collection,
    )


@pytest.fixture
def postgres_bulk_transactions(db_session):
    return BulkTransactionsClient(session=db_session)


@pytest.fixture
def api_client(db_session):
    return StacApi(
        settings=PostgresSettings(),
        client=CoreCrudClient(session=db_session),
        extensions=[
            TransactionExtension(client=TransactionsClient(session=db_session)),
            ContextExtension(),
            SortExtension(),
            FieldsExtension(),
            QueryExtension(),
        ],
    )


@pytest.fixture
def app_client(api_client, load_test_data, postgres_transactions):
    coll = Collection.parse_obj(load_test_data("test_collection.json"))
    postgres_transactions.create_collection(coll, request=MockStarletteRequest)

    with TestClient(api_client.app) as test_app:
        yield test_app

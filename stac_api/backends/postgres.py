from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from stac_api.backends import StacBackend

class PostgresBackend(StacBackend):

    async def on_startup(self):
        """Create database engines and sessions on startup"""
        self.state.ENGINE_READER = create_engine(
            self.state.settings.reader_connection_string, echo=self.state.settings.debug
        )
        self.state.ENGINE_WRITER = create_engine(
            self.state.settings.writer_connection_string, echo=self.state.settings.debug
        )
        self.state.DB_READER = sessionmaker(
            autocommit=False, autoflush=False, bind=self.state.ENGINE_READER
        )
        self.state.DB_WRITER = sessionmaker(
            autocommit=False, autoflush=False, bind=self.state.ENGINE_WRITER
        )

    async def on_shutdown(self):
        """Dispose of database engines and sessions on app shutdown"""
        self.state.ENGINE_READER.dispose()
        self.state.ENGINE_WRITER.dispose()


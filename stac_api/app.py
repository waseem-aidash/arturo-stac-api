"""FastAPI application."""
import asyncio
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi.logger import logger
from stac_api.api import create_app
from stac_api.config import ApiSettings
from starlette.requests import Request

gunicorn_logger = logging.getLogger("gunicorn.error")
logger.handlers = gunicorn_logger.handlers
logger.setLevel(logging.INFO)

os.environ["AWS_REQUEST_PAYER"] = "requester"


settings = ApiSettings(
    stac_api_extensions=["context", "fields", "query", "sort", "transaction"],
    add_ons=["tiles"],
    default_includes={
        "id",
        "type",
        "geometry",
        "bbox",
        "links",
        "assets",
        "properties.datetime",
        "properties.updated",
        "properties.created",
        "properties.gsd",
        "properties.eo:bands",
        "properties.proj:epsg",
        "properties.naip:quadrant",
        "properties.naip:cell_id",
        "properties.naip:statename",
        "properties.naip:utm_zone",
        "properties.naip:quad_location",
    },
)
app = create_app(settings=settings)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """log request time"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Request to {request.url.path} took {process_time} seconds")
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")
async def set_workers_per_thread():
    """set number of workers per thread"""
    logger.info(f"cpu count: {os.cpu_count()}")
    loop = asyncio.get_running_loop()
    workers_per_thread = int(os.getenv("THREADS_PER_WORKER", 2 * os.cpu_count() + 1))
    logger.info(f"workers per thread: {workers_per_thread}")
    loop.set_default_executor(ThreadPoolExecutor(max_workers=workers_per_thread))

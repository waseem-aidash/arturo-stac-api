"""FastAPI application."""
import logging
import os
import time

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

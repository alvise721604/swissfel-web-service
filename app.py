from fastapi import Request, HTTPException
from nicegui import ui

from config import settings
from pages.cleanup import build_cleanup_page
from pages.home import build_home
from pages.reservations import build_reservations_page
from pages.status import build_status_page


@ui.page('/')
def home(request: Request):
    build_home(request)


@ui.page('/reservations')
def reservations(request: Request):
    build_reservations_page(request)


@ui.page('/status')
def status(request: Request):
    build_status_page(request)


@ui.page('/cleanup')
def cleanup(request: Request):
    build_cleanup_page(request)


ui.run(
    title=settings.app_title,
    host=settings.host,
    port=settings.port,
    reload=False,
)

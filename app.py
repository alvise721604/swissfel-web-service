from fastapi import Request, HTTPException
from nicegui import ui

from config import settings
from pages.cleanup import build_cleanup_page
from pages.home import build_home
from pages.createreservation import build_reservation_page
from pages.deletereservation import delete_reservation_page
from pages.listreservations import list_reservations_page
from pages.status import build_status_page


@ui.page('/')
def home(request: Request):
    build_home(request)


@ui.page('/createreservation')
def createreservation(request: Request):
    build_reservation_page(request)

@ui.page('/deletereservation')
def deletereservation(request: Request):
    delete_reservation_page(request)

@ui.page('/listreservations')
def listreservations(request: Request):
    list_reservations_page(request)

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

from contextlib import contextmanager

from fastapi import Request
from nicegui import ui

from services.auth import get_current_username


def header(title: str, request: Request) -> None:
    username = get_current_username(request)

    with ui.header().classes('items-center justify-between'):
        ui.label(title).classes('text-xl font-bold')
        with ui.row().classes('items-center gap-2'):
            ui.label(f'User: {username}').classes('text-sm')
            ui.button('Home', on_click=lambda: ui.navigate.to('/'))
            ui.button('Reservations', on_click=lambda: ui.navigate.to('/reservations'))
            ui.button('Status', on_click=lambda: ui.navigate.to('/status'))
            ui.button('Cleanup', on_click=lambda: ui.navigate.to('/cleanup'))


@contextmanager
def page_container(title: str, request: Request):
    header(title, request)
    with ui.column().classes('w-full max-w-6xl mx-auto p-4 gap-4'):
        yield

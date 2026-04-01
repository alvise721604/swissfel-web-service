from fastapi import Request
from nicegui import ui

from pages.common import page_container


def build_home(request: Request) -> None:
    with page_container('User Services', request):
        ui.label('User Services').classes('text-3xl font-bold')
        ui.label('Internal operational tool based on NiceGUI')

        with ui.row().classes('gap-4'):

            with ui.card().classes('w-80'):
                ui.label('Cluster Status').classes('text-lg font-semibold')
                ui.label('Show partitions and jobs')
                ui.button('Open', on_click=lambda: ui.navigate.to('/status'))

            with ui.card().classes('w-80'):
                ui.label('List Reservations').classes('text-lg font-semibold')
                ui.label('List Slurm reservations')
                ui.button('Open', on_click=lambda: ui.navigate.to('/listreservations'))

            with ui.card().classes('w-80'):
                ui.label('Create Reservation').classes('text-lg font-semibold')
                ui.label('Create Slurm reservation')
                ui.button('Open', on_click=lambda: ui.navigate.to('/createreservations'))

            with ui.card().classes('w-80'):
                ui.label('Delete Reservation').classes('text-lg font-semibold')
                ui.label('Delete Slurm reservation')
                ui.button('Open', on_click=lambda: ui.navigate.to('/deletereservation'))

            with ui.card().classes('w-80'):
                ui.label('Cleanup PGROUP').classes('text-lg font-semibold')
                ui.label('Launch cleanup in dry-run or real delete')
                ui.button('Open', on_click=lambda: ui.navigate.to('/cleanup'))

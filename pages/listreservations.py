from fastapi import Request
from nicegui import ui

from pages.common import page_container
from services.jobs import list_jobs
from services.ra_api import fetch_cluster_status, fetch_reservation_details

def get_reservations() -> list[str]:
    """Per ora statico; poi potrai sostituirlo con una vera chiamata REST."""
    return [
        'res-admin-001',
        'res-gpu-002',
        'res-weekend-003',
    ]

def _to_pretty_rows(data: dict) -> list[dict]:
    rows = []
    for key, value in data.items():
        rows.append({
            'field': str(key),
            'value': str(value),
        })
    return rows

def list_reservations_page(request: Request) -> None:
    with page_container('List Reservations', request):
        ui.label('List Reservations').classes('text-2xl font-bold')

    reservations = get_reservations()

    selected_reservation = ui.select(
        options=reservations,
        label='Reservation',
        #with_input=True,
    ).classes('w-96')

    details_container = ui.column().classes('w-full gap-4')

    def load_reservation_details() -> None:
        details_container.clear()

        if not selected_reservation.value:
            with details_container:
                ui.label('Please select a reservation first.').classes('text-red-600')
            return

        try:
            details = fetch_reservation_details(selected_reservation.value)

            with details_container:
                ui.label(f"Reservation details: {selected_reservation.value}") \
                    .classes('text-lg font-semibold')

                if not details:
                    ui.label('No details returned by RA API.')
                    return

                columns = [
                    {'name': 'field', 'label': 'Field', 'field': 'field', 'required': True},
                    {'name': 'value', 'label': 'Value', 'field': 'value'},
                ]
                rows = _to_pretty_rows(details)

                ui.table(
                    columns=columns,
                    rows=rows,
                    row_key='field',
                    pagination=20,
                ).classes('w-full')

        except Exception as err:
            with details_container:
                ui.label(f'Error while loading reservation details: {err}') \
                    .classes('text-red-600')

    with ui.row().classes('items-end gap-3'):
        selected_reservation
        ui.button('Load details', on_click=load_reservation_details)

    ui.separator().classes('w-full mt-4 mb-2')

    with details_container:
        ui.label('Select a reservation and click "Load details".').classes('text-gray-600')
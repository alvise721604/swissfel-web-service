from fastapi import Request
from nicegui import ui

from config import settings
from models import ReservationForm
from pages.common import page_container
from services.auth import get_current_username
from services.ldap_service import user_can_manage_pgroup
from services.ra_api import create_reservation


def build_reservation_page(request: Request) -> None:
    with page_container('Create Reservation', request):
        ui.label('Create Slurm Reservation').classes('text-2xl font-bold')
        result_box = ui.column().classes('w-full')

        with ui.card().classes('w-full max-w-xl'):
            pgroup = ui.input('PGROUP').props('clearable').classes('w-full')
            partition = ui.select(
                settings.allowed_partitions,
                value=settings.allowed_partitions[0],
                label='Partition',
            ).classes('w-full')
            nodes = ui.number(
                'Nodes',
                value=1,
                min=settings.min_nodes,
                max=settings.max_nodes,
                precision=0,
            ).classes('w-full')
            days = ui.number(
                'Days',
                value=1,
                min=settings.min_days,
                max=settings.max_days,
                precision=0,
            ).classes('w-full')

            async def submit() -> None:
                result_box.clear()
                username = get_current_username(request)

                try:
                    form = ReservationForm(
                        pgroup=(pgroup.value or '').strip(),
                        partition=partition.value,
                        nodes=int(nodes.value),
                        days=int(days.value),
                    )
                except Exception:
                    ui.notify('Invalid values in form', type='negative')
                    return

                errors = form.validate(
                    allowed_partitions=settings.allowed_partitions,
                    min_nodes=settings.min_nodes,
                    max_nodes=settings.max_nodes,
                    min_days=settings.min_days,
                    max_days=settings.max_days,
                )
                if errors:
                    for err in errors:
                        ui.notify(err, type='negative')
                    return

                if not user_can_manage_pgroup(username, form.pgroup):
                    ui.notify(
                        f'User {username} is not authorized to manage {form.pgroup}',
                        type='negative',
                    )
                    return

                try:
                    result = await create_reservation(
                        pgroup=form.pgroup,
                        partition=form.partition,
                        nodes=form.nodes,
                        days=form.days,
                    )
                    ui.notify('Reservation created', type='positive')

                    with result_box:
                        with ui.card().classes('w-full'):
                            ui.label('Result').classes('text-lg font-semibold')
                            for key in (
                                'reservation_name',
                                'pgroup',
                                'partition',
                                'nodes',
                                'start',
                                'end',
                                'status',
                            ):
                                if key in result:
                                    ui.label(f'{key}: {result[key]}')

                except Exception as e:
                    ui.notify(f'Error during creation: {e}', type='negative')

            ui.button('Create Reservation', on_click=submit)

from fastapi import Request
from nicegui import ui

from models import CleanupForm
from pages.common import page_container
from services.auth import get_current_username
from services.jobs import submit_cleanup_job
from services.ldap_service import user_can_manage_pgroup


def build_cleanup_page(request: Request) -> None:
    with page_container('Cleanup PGROUP', request):
        ui.label('Cleanup PGROUP').classes('text-2xl font-bold')

        with ui.card().classes('w-full max-w-xl'):
            beamline = ui.input('Beamline').classes('w-full')
            pgroup = ui.input('PGROUP').classes('w-full')
            pattern = ui.input('Pattern (optional)').classes('w-full')
            real_delete = ui.checkbox('Real delete', value=False)

            async def submit() -> None:
                username = get_current_username(request)

                form = CleanupForm(
                    beamline=(beamline.value or '').strip(),
                    pgroup=(pgroup.value or '').strip(),
                    pattern=(pattern.value or '').strip(),
                    real_delete=bool(real_delete.value),
                )

                errors = form.validate()
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

                def confirmed() -> None:
                    job_id = submit_cleanup_job(
                        username=username,
                        beamline=form.beamline,
                        pgroup=form.pgroup,
                        pattern=form.pattern,
                        real_delete=form.real_delete,
                    )
                    ui.notify(f'Job accepted: {job_id}', type='positive')
                    ui.navigate.to('/status')

                msg = (
                    f'Confirm cleanup for {form.beamline}:{form.pgroup}'
                    + (' [REAL DELETE]' if form.real_delete else ' [DRY RUN]')
                    + '?'
                )

                with ui.dialog() as dialog, ui.card():
                    ui.label(msg)
                    with ui.row():
                        ui.button('Cancel', on_click=dialog.close)
                        ui.button('Confirm', on_click=lambda: (dialog.close(), confirmed()))

                dialog.open()

            ui.button('Submit cleanup', on_click=submit)

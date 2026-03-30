# from fastapi import Request
# from nicegui import ui

# from pages.common import page_container
# from services.jobs import list_jobs
# from services.ra_api import fetch_cluster_status


# @ui.refreshable
# def cluster_table() -> None:
#     rows = fetch_cluster_status()
#     columns = [
#         {'name': 'partition', 'label': 'Partition', 'field': 'partition', 'required': True},
#         {'name': 'nodes', 'label': 'Nodes', 'field': 'nodes'},
#         {'name': 'reservations', 'label': 'Reservations', 'field': 'reservations'},
#     ]
#     ui.table(columns=columns, rows=rows, row_key='partition').classes('w-full')


# @ui.refreshable
# def jobs_table() -> None:
#     rows = list_jobs()
#     columns = [
#         {'name': 'job_id', 'label': 'Job ID', 'field': 'job_id', 'required': True},
#         {'name': 'kind', 'label': 'Kind', 'field': 'kind'},
#         {'name': 'username', 'label': 'User', 'field': 'username'},
#         {'name': 'beamline', 'label': 'Beamline', 'field': 'beamline'},
#         {'name': 'pgroup', 'label': 'PGROUP', 'field': 'pgroup'},
#         {'name': 'status', 'label': 'Status', 'field': 'status'},
#         {'name': 'result', 'label': 'Result', 'field': 'result'},
#         {'name': 'created_at', 'label': 'Created', 'field': 'created_at'},
#         {'name': 'started_at', 'label': 'Started', 'field': 'started_at'},
#         {'name': 'finished_at', 'label': 'Finished', 'field': 'finished_at'},
#     ]
#     ui.table(columns=columns, rows=rows, row_key='job_id').classes('w-full')


# def build_status_page(request: Request) -> None:
#     with page_container('Status', request):
#         ui.label('Cluster Status').classes('text-2xl font-bold')

#         with ui.row().classes('gap-2'):
#             ui.button('Refresh cluster', on_click=cluster_table.refresh)
#             ui.button('Refresh jobs', on_click=jobs_table.refresh)

#         ui.label('Partitions').classes('text-lg font-semibold')
#         cluster_table()

#         ui.separator()

#         ui.label('Jobs').classes('text-lg font-semibold')
#         jobs_table()

#         ui.timer(5.0, jobs_table.refresh)


from fastapi import Request
from nicegui import ui

from pages.common import page_container
from services.jobs import list_jobs
from services.ra_api import fetch_cluster_status


def _format_nodes(value) -> str:
    if value is None:
        return ''
    if isinstance(value, list):
        return ', '.join(str(v) for v in value)
    if isinstance(value, dict):
        return ', '.join(f'{k}={v}' for k, v in value.items())
    return str(value)


@ui.refreshable
def cluster_table() -> None:
    raw_rows = fetch_cluster_status()

    rows = []
    for row in raw_rows:
        rows.append({
            'name': row.get('name', ''),
            'totcores': row.get('totcores', ''),
            'totnodes': row.get('totnodes', ''),
            'totgpus': row.get('totgpus', ''),
            'res': row.get('res', ''),
            'state': row.get('state', ''),
            'max_job_duration': row.get('max_job_duration', ''),
            'nodes': _format_nodes(row.get('nodes')),
        })

    columns = [
        {'name': 'name', 'label': 'Partition', 'field': 'name', 'required': True},
        {'name': 'state', 'label': 'State', 'field': 'state'},
        {'name': 'totnodes', 'label': 'Total Nodes', 'field': 'totnodes'},
        {'name': 'totcores', 'label': 'Total Cores', 'field': 'totcores'},
        {'name': 'totgpus', 'label': 'Total GPUs', 'field': 'totgpus'},
        {'name': 'max_job_duration', 'label': 'Max Job Duration', 'field': 'max_job_duration'},
        {'name': 'res', 'label': 'Resources', 'field': 'res'},
        {'name': 'nodes', 'label': 'Configured Nodes', 'field': 'nodes'},
    ]

    ui.table(columns=columns, rows=rows, row_key='name').classes('w-full')


@ui.refreshable
def jobs_table() -> None:
    rows = list_jobs()
    columns = [
        {'name': 'job_id', 'label': 'Job ID', 'field': 'job_id', 'required': True},
        {'name': 'kind', 'label': 'Kind', 'field': 'kind'},
        {'name': 'username', 'label': 'User', 'field': 'username'},
        {'name': 'beamline', 'label': 'Beamline', 'field': 'beamline'},
        {'name': 'pgroup', 'label': 'PGROUP', 'field': 'pgroup'},
        {'name': 'status', 'label': 'Status', 'field': 'status'},
        {'name': 'result', 'label': 'Result', 'field': 'result'},
        {'name': 'created_at', 'label': 'Created', 'field': 'created_at'},
        {'name': 'started_at', 'label': 'Started', 'field': 'started_at'},
        {'name': 'finished_at', 'label': 'Finished', 'field': 'finished_at'},
    ]
    ui.table(columns=columns, rows=rows, row_key='job_id').classes('w-full')


def build_status_page(request: Request) -> None:
    with page_container('Status', request):
        ui.label('Cluster Status').classes('text-2xl font-bold')

        with ui.row().classes('gap-2'):
            ui.button('Refresh cluster', on_click=cluster_table.refresh)
            ui.button('Refresh jobs', on_click=jobs_table.refresh)

        ui.label('Partitions').classes('text-lg font-semibold')
        cluster_table()

        ui.separator()

        ui.label('Jobs').classes('text-lg font-semibold')
        jobs_table()

        ui.timer(5.0, jobs_table.refresh)
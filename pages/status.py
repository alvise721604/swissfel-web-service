from fastapi import Request
from nicegui import ui

from pages.common import page_container
from services.jobs import list_jobs
from services.ra_api import fetch_cluster_status


def _to_text(value) -> str:
    if value is None:
        return ''
    if isinstance(value, (list, tuple)):
        return ', '.join(str(v) for v in value)
    if isinstance(value, dict):
        return ', '.join(f'{k}={v}' for k, v in value.items())
    return str(value)


def _normalize_nodes(raw_nodes) -> list[dict]:
    """Converte configured_nodes in una lista di dict uniforme per la tabella dettagli nodi."""
    result = []

    if raw_nodes is None:
        return result

    # Caso 1: lista di stringhe o lista di dict
    if isinstance(raw_nodes, list):
        for item in raw_nodes:
            if isinstance(item, dict):
                node_name = (
                    item.get('name')
                    or item.get('node')
                    or item.get('hostname')
                    or item.get('host')
                    or ''
                )
                result.append({
                    'node_name': node_name,
                    'state': _to_text(item.get('state', '')),
                    'cores': _to_text(item.get('cores', '')),
                    'gpus': _to_text(item.get('gpus', '')),
                    'resources': _to_text(item.get('resources', '')),
                    'raw': _to_text(item),
                })
            else:
                result.append({
                    'node_name': str(item),
                    'state': '',
                    'cores': '',
                    'gpus': '',
                    'resources': '',
                    'raw': '',
                })
        return result

    # Caso 2: dict tipo {node01: {...}, node02: {...}}
    if isinstance(raw_nodes, dict):
        for node_name, node_info in raw_nodes.items():
            if isinstance(node_info, dict):
                result.append({
                    'node_name': str(node_name),
                    'state': _to_text(node_info.get('state', '')),
                    'cores': _to_text(node_info.get('cores', '')),
                    'gpus': _to_text(node_info.get('gpus', '')),
                    'resources': _to_text(node_info.get('resources', '')),
                    'raw': _to_text(node_info),
                })
            else:
                result.append({
                    'node_name': str(node_name),
                    'state': _to_text(node_info),
                    'cores': '',
                    'gpus': '',
                    'resources': '',
                    'raw': '',
                })
        return result

    # Caso 3: valore singolo
    result.append({
        'node_name': _to_text(raw_nodes),
        'state': '',
        'cores': '',
        'gpus': '',
        'resources': '',
        'raw': '',
    })
    return result


def _normalize_partition(row: dict) -> dict:
    nodes_detail = _normalize_nodes(row.get('nodes'))

    return {
        'name': row.get('name', ''),
        'state': row.get('state', ''),
        'totnodes': row.get('totnodes', ''),
        'totcores': row.get('totcores', ''),
        'totgpus': row.get('totgpus', ''),
        'max_job_duration': row.get('max_job_duration', ''),
        'res': _to_text(row.get('res')),
        'nodes_count': len(nodes_detail),
        'nodes_detail': nodes_detail,
        'nodes_preview': ', '.join(n['node_name'] for n in nodes_detail[:6]) + (' ...' if len(nodes_detail) > 6 else ''),
    }


@ui.refreshable
def cluster_table() -> None:
    raw_rows = fetch_cluster_status()
    partitions = [_normalize_partition(row) for row in raw_rows]

    summary_rows = [
        {
            'name': p['name'],
            'state': p['state'],
            'totnodes': p['totnodes'],
            'totcores': p['totcores'],
            'totgpus': p['totgpus'],
            'max_job_duration': p['max_job_duration'],
            'nodes_count': p['nodes_count'],
        }
        for p in partitions
    ]

    summary_columns = [
        {'name': 'name', 'label': 'Partition', 'field': 'name', 'required': True},
        {'name': 'state', 'label': 'State', 'field': 'state'},
        {'name': 'totnodes', 'label': 'Nodes', 'field': 'totnodes'},
        {'name': 'totcores', 'label': 'Cores', 'field': 'totcores'},
        {'name': 'totgpus', 'label': 'GPUs', 'field': 'totgpus'},
        {'name': 'max_job_duration', 'label': 'Max Job Duration', 'field': 'max_job_duration'},
        {'name': 'nodes_count', 'label': 'Configured Nodes', 'field': 'nodes_count'},
    ]

    node_columns = [
        {'name': 'node_name', 'label': 'Node', 'field': 'node_name', 'required': True},
        {'name': 'state', 'label': 'State', 'field': 'state'},
        {'name': 'cores', 'label': 'Cores', 'field': 'cores'},
        {'name': 'gpus', 'label': 'GPUs', 'field': 'gpus'},
        {'name': 'resources', 'label': 'Resources', 'field': 'resources'},
        {'name': 'raw', 'label': 'Raw Details', 'field': 'raw'},
    ]

    with ui.column().classes('w-full gap-4'):

        ui.table(
            columns=summary_columns,
            rows=summary_rows,
            row_key='name',
            pagination=10,
        ).classes('w-full')

        selected_label = ui.label('Node details: seleziona una partizione dai pannelli qui sotto').classes(
            'text-lg font-semibold'
        )

        node_table = ui.table(
            columns=node_columns,
            rows=[],
            row_key='node_name',
            pagination=20,
        ).classes('w-full')

        def show_nodes(partition: dict) -> None:
            selected_label.set_text(f"Node details: {partition['name']}")
            node_table.rows = partition['nodes_detail']
            node_table.update()

        ui.label('Partition details').classes('text-lg font-semibold')

        for partition in partitions:
            title = (
                f"{partition['name']}  |  "
                f"state={partition['state']}  |  "
                f"nodes={partition['totnodes']}  |  "
                f"cores={partition['totcores']}  |  "
                f"gpus={partition['totgpus']}"
            )

            with ui.expansion(title, icon='dns').classes('w-full'):
                with ui.grid(columns=2).classes('w-full gap-4'):
                    with ui.card().classes('w-full'):
                        ui.label('General').classes('text-md font-bold')
                        ui.label(f"Partition: {partition['name']}")
                        ui.label(f"State: {partition['state']}")
                        ui.label(f"Max job duration: {partition['max_job_duration']}")

                        with ui.column().classes('w-full gap-1'):
                            ui.label('Resources:').classes('font-medium')
                            ui.label(partition['res']).classes(
                                'w-full text-sm whitespace-normal break-all'
                            )
                    # with ui.card().classes('w-full'):
                    #     ui.label('General').classes('text-md font-bold')
                    #     ui.label(f"Partition: {partition['name']}")
                    #     ui.label(f"State: {partition['state']}")
                    #     ui.label(f"Max job duration: {partition['max_job_duration']}")
                    #     #ui.label(f"Resources: {partition['res']}")
                    #     ui.label(f"Resources: {partition['res']}").classes(
                    #         'w-full whitespace-normal break-words'
                    #         )

                    with ui.card().classes('w-full'):
                        ui.label('Capacity').classes('text-md font-bold')
                        ui.label(f"Total nodes: {partition['totnodes']}")
                        ui.label(f"Total cores: {partition['totcores']}")
                        ui.label(f"Total GPUs: {partition['totgpus']}")
                        ui.label(f"Configured nodes: {partition['nodes_count']}")

                with ui.row().classes('items-center gap-3 mt-3'):
                    ui.button(
                        f"Show nodes for {partition['name']}",
                        on_click=lambda p=partition: show_nodes(p),
                        icon='visibility',
                    )
                    ui.label(
                        f"Preview: {partition['nodes_preview'] or 'no node list available'}"
                    ).classes('text-sm text-gray-600')


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
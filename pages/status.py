from fastapi import Request
from nicegui import ui

from pages.common import page_container
from services.jobs import list_jobs
from services.ra_api import fetch_cluster_status

def _split_top_level_commas(text: str) -> list[str]:
    """Divide una stringa sulle virgole, ma ignorando quelle dentro [...]"""
    parts = []
    current = []
    bracket_level = 0

    for ch in text:
        if ch == '[':
            bracket_level += 1
            current.append(ch)
        elif ch == ']':
            bracket_level -= 1
            current.append(ch)
        elif ch == ',' and bracket_level == 0:
            part = ''.join(current).strip()
            if part:
                parts.append(part)
            current = []
        else:
            current.append(ch)

    part = ''.join(current).strip()
    if part:
        parts.append(part)

    return parts


def _count_bracket_expression(expr: str) -> int:
    """
    Conta quanti nodi rappresenta una espressione tipo:
    051-053,055-059,164
    """
    total = 0
    for item in expr.split(','):
        item = item.strip()
        if not item:
            continue

        if '-' in item:
            start, end = item.split('-', 1)
            try:
                total += int(end) - int(start) + 1
            except ValueError:
                total += 1
        else:
            total += 1

    return total


def _count_configured_nodes(raw_nodes) -> int:
    """
    Conta i nodi configurati a partire da:
    - lista
    - dict
    - stringa hostlist compressa stile SLURM
    """
    if raw_nodes is None:
        return 0

    if isinstance(raw_nodes, list):
        return len(raw_nodes)

    if isinstance(raw_nodes, dict):
        return len(raw_nodes)

    if isinstance(raw_nodes, str):
        raw_nodes = raw_nodes.strip()
        if not raw_nodes:
            return 0

        total = 0
        chunks = _split_top_level_commas(raw_nodes)

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            m = re.search(r'\[(.*?)\]', chunk)
            if m:
                total += _count_bracket_expression(m.group(1))
            else:
                total += 1

        return total

    return 1

def _to_text(value) -> str:
    if value is None:
        return ''
    if isinstance(value, (list, tuple)):
        return ', '.join(str(v) for v in value)
    if isinstance(value, dict):
        return ', '.join(f'{k}={v}' for k, v in value.items())
    return str(value)

def _normalize_nodes(raw_nodes) -> list[dict]:
    result = []

    if raw_nodes is None:
        return result

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

    if isinstance(raw_nodes, str):
        result.append({
            'node_name': raw_nodes,
            'state': '',
            'cores': '',
            'gpus': '',
            'resources': '',
            'raw': '',
        })
        return result

    result.append({
        'node_name': _to_text(raw_nodes),
        'state': '',
        'cores': '',
        'gpus': '',
        'resources': '',
        'raw': '',
    })
    return result

# def _normalize_nodes(raw_nodes) -> list[dict]:
#     """Converte configured_nodes in una lista di dict uniforme per la tabella dettagli nodi."""
#     result = []

#     if raw_nodes is None:
#         return result

#     # Caso 1: lista di stringhe o lista di dict
#     if isinstance(raw_nodes, list):
#         for item in raw_nodes:
#             if isinstance(item, dict):
#                 node_name = (
#                     item.get('name')
#                     or item.get('node')
#                     or item.get('hostname')
#                     or item.get('host')
#                     or ''
#                 )
#                 result.append({
#                     'node_name': node_name,
#                     'state': _to_text(item.get('state', '')),
#                     'cores': _to_text(item.get('cores', '')),
#                     'gpus': _to_text(item.get('gpus', '')),
#                     'resources': _to_text(item.get('resources', '')),
#                     'raw': _to_text(item),
#                 })
#             else:
#                 result.append({
#                     'node_name': str(item),
#                     'state': '',
#                     'cores': '',
#                     'gpus': '',
#                     'resources': '',
#                     'raw': '',
#                 })
#         return result

#     # Caso 2: dict tipo {node01: {...}, node02: {...}}
#     if isinstance(raw_nodes, dict):
#         for node_name, node_info in raw_nodes.items():
#             if isinstance(node_info, dict):
#                 result.append({
#                     'node_name': str(node_name),
#                     'state': _to_text(node_info.get('state', '')),
#                     'cores': _to_text(node_info.get('cores', '')),
#                     'gpus': _to_text(node_info.get('gpus', '')),
#                     'resources': _to_text(node_info.get('resources', '')),
#                     'raw': _to_text(node_info),
#                 })
#             else:
#                 result.append({
#                     'node_name': str(node_name),
#                     'state': _to_text(node_info),
#                     'cores': '',
#                     'gpus': '',
#                     'resources': '',
#                     'raw': '',
#                 })
#         return result

#     # Caso 3: valore singolo
#     result.append({
#         'node_name': _to_text(raw_nodes),
#         'state': '',
#         'cores': '',
#         'gpus': '',
#         'resources': '',
#         'raw': '',
#     })
#     return result


def _normalize_partition(row: dict) -> dict:
    nodes_detail = _normalize_nodes(row.get('configured_nodes'))

    return {
        'name': row.get('name', ''),
        'state': row.get('state', ''),
        'totnodes': row.get('totnodes', ''),
        'totcores': row.get('totcores', ''),
        'totgpus': row.get('totgpus', ''),
        'max_job_duration': row.get('max_job_duration', ''),
        'res': _to_text(row.get('res')),
        'nodes_count': len(nodes_detail),
        #'nodes_count': _count_configured_nodes(row.get('nodes')),
        'nodes_detail': nodes_detail,
        'nodes_preview': ', '.join(n['node_name'] for n in nodes_detail[:6]) + (' ...' if len(nodes_detail) > 6 else ''),
    }


# @ui.refreshable
# def cluster_table() -> None:
#     raw_rows = fetch_cluster_status()
#     partitions = [_normalize_partition(row) for row in raw_rows]

#     summary_rows = [
#         {
#             'name': p['name'],
#             'state': p['state'],
#             'totnodes': p['totnodes'],
#             'totcores': p['totcores'],
#             'totgpus': p['totgpus'],
#             'max_job_duration': p['max_job_duration'],
#             'nodes_count': p['nodes_count'],
#         }
#         for p in partitions
#     ]

#     summary_columns = [
#         {'name': 'name', 'label': 'Partition', 'field': 'name', 'required': True},
#         {'name': 'state', 'label': 'State', 'field': 'state'},
#         {'name': 'totnodes', 'label': 'Nodes', 'field': 'totnodes'},
#         {'name': 'totcores', 'label': 'Cores', 'field': 'totcores'},
#         {'name': 'totgpus', 'label': 'GPUs', 'field': 'totgpus'},
#         {'name': 'max_job_duration', 'label': 'Max Job Duration', 'field': 'max_job_duration'},
#         {'name': 'nodes_count', 'label': 'Configured Nodes', 'field': 'nodes_count'},
#     ]

#     node_columns = [
#         {'name': 'node_name', 'label': 'Node', 'field': 'node_name', 'required': True},
#         {'name': 'state', 'label': 'State', 'field': 'state'},
#         {'name': 'cores', 'label': 'Cores', 'field': 'cores'},
#         {'name': 'gpus', 'label': 'GPUs', 'field': 'gpus'},
#         {'name': 'resources', 'label': 'Resources', 'field': 'resources'},
#         {'name': 'raw', 'label': 'Raw Details', 'field': 'raw'},
#     ]

#     with ui.column().classes('w-full gap-4'):

#         ui.table(
#             columns=summary_columns,
#             rows=summary_rows,
#             row_key='name',
#             pagination=10,
#         ).classes('w-full')

#         selected_label = ui.label('Node details: seleziona una partizione dai pannelli qui sotto').classes(
#             'text-lg font-semibold'
#         )

#         node_table = ui.table(
#             columns=node_columns,
#             rows=[],
#             row_key='node_name',
#             pagination=20,
#         ).classes('w-full')

#         def show_nodes(partition: dict) -> None:
#             selected_label.set_text(f"Node details: {partition['name']}")
#             node_table.rows = partition['nodes_detail']
#             node_table.update()

#         ui.label('Partition details').classes('text-lg font-semibold')

#         for partition in partitions:
#             title = (
#                 f"{partition['name']}  |  "
#                 f"state={partition['state']}  |  "
#                 f"nodes={partition['totnodes']}  |  "
#                 f"cores={partition['totcores']}  |  "
#                 f"gpus={partition['totgpus']}"
#             )

#             with ui.expansion(title, icon='dns').classes('w-full'):
#                 with ui.grid(columns=2).classes('w-full gap-4'):
#                     with ui.card().classes('w-full'):
#                         ui.label('General').classes('text-md font-bold')
#                         ui.label(f"Partition: {partition['name']}")
#                         ui.label(f"State: {partition['state']}")
#                         ui.label(f"Max job duration: {partition['max_job_duration']}")

#                         with ui.column().classes('w-full gap-1'):
#                             ui.label('Resources:').classes('font-medium')
#                             ui.label(partition['res']).classes(
#                                 'w-full text-sm whitespace-normal break-all'
#                             )
#                     # with ui.card().classes('w-full'):
#                     #     ui.label('General').classes('text-md font-bold')
#                     #     ui.label(f"Partition: {partition['name']}")
#                     #     ui.label(f"State: {partition['state']}")
#                     #     ui.label(f"Max job duration: {partition['max_job_duration']}")
#                     #     #ui.label(f"Resources: {partition['res']}")
#                     #     ui.label(f"Resources: {partition['res']}").classes(
#                     #         'w-full whitespace-normal break-words'
#                     #         )

#                     with ui.card().classes('w-full'):
#                         ui.label('Capacity').classes('text-md font-bold')
#                         ui.label(f"Total nodes: {partition['totnodes']}")
#                         ui.label(f"Total cores: {partition['totcores']}")
#                         ui.label(f"Total GPUs: {partition['totgpus']}")
#                         ui.label(f"Configured nodes: {partition['nodes_count']}")

#                 with ui.row().classes('items-center gap-3 mt-3'):
#                     ui.button(
#                         f"Show nodes for {partition['name']}",
#                         on_click=lambda p=partition: show_nodes(p),
#                         icon='visibility',
#                     )
#                     ui.label(
#                         f"Preview: {partition['nodes_preview'] or 'no node list available'}"
#                     ).classes('text-sm text-gray-600')




def _to_text(value) -> str:
    if value is None:
        return ''
    if isinstance(value, (list, tuple)):
        return ', '.join(str(v) for v in value)
    if isinstance(value, dict):
        return ', '.join(f'{k}={v}' for k, v in value.items())
    return str(value)


def _normalize_nodes(raw_nodes) -> list[dict]:
    result = []

    if raw_nodes is None:
        return result

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

    if isinstance(raw_nodes, str):
        result.append({
            'node_name': raw_nodes,
            'state': '',
            'cores': '',
            'gpus': '',
            'resources': '',
            'raw': '',
        })
        return result

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
    nodes_detail = _normalize_nodes(row.get('configured_nodes'))

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
            #'nodes_count': p['nodes_count'],
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
        #{'name': 'nodes_count', 'label': 'Configured Nodes', 'field': 'nodes_count'},
    ]

    node_columns = [
        {'name': 'node_name', 'label': 'Node', 'field': 'node_name', 'required': True},
        {'name': 'state', 'label': 'State', 'field': 'state'},
        {'name': 'cores', 'label': 'Cores', 'field': 'cores'},
        {'name': 'gpus', 'label': 'GPUs', 'field': 'gpus'},
        {'name': 'resources', 'label': 'Resources', 'field': 'resources'},
        {'name': 'raw', 'label': 'Raw Details', 'field': 'raw'},
    ]

    ui.table(
        columns=summary_columns,
        rows=summary_rows,
        row_key='name',
        pagination=5,
    ).classes('w-full')

    ui.label('Partition details').classes('text-lg font-semibold mt-4')

    for partition in partitions:
        title = (
            f"{partition['name']} | "
            f"state={partition['state']} | "
            f"nodes={partition['totnodes']} | "
            f"cores={partition['totcores']} | "
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

                with ui.card().classes('w-full'):
                    ui.label('Capacity').classes('text-md font-bold')
                    ui.label(f"Total nodes: {partition['totnodes']}")
                    ui.label(f"Total cores: {partition['totcores']}")
                    ui.label(f"Total GPUs: {partition['totgpus']}")
                    #ui.label(f"Configured nodes: {partition['nodes_count']}")

            ui.separator().classes('my-4')
            ui.label('Node details').classes('text-md font-bold')

            if len(partition['nodes_detail']) == 1 and not any([
                partition['nodes_detail'][0]['state'],
                partition['nodes_detail'][0]['cores'],
                partition['nodes_detail'][0]['gpus'],
                partition['nodes_detail'][0]['resources'],
                partition['nodes_detail'][0]['raw'],
            ]):
                with ui.card().classes('w-full'):
                    ui.label('Configured node expression').classes('font-medium')
                    ui.label(partition['nodes_detail'][0]['node_name']).classes(
                        'w-full text-sm whitespace-normal break-all'
                    )
            else:
                ui.table(
                    columns=node_columns,
                    rows=partition['nodes_detail'],
                    row_key='node_name',
                    pagination=20,
                ).classes('w-full')

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
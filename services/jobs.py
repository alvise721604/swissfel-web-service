import asyncio
import threading
import uuid
from datetime import datetime

from services.cleanup_runner import run_cleanup_command


_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _now() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def _update_job(job_id: str, **updates) -> None:
    with _jobs_lock:
        if job_id in _jobs:
            _jobs[job_id].update(updates)


def list_jobs() -> list[dict]:
    with _jobs_lock:
        return sorted(
            [dict(job) for job in _jobs.values()],
            key=lambda x: x['created_at'],
            reverse=True,
        )


def create_job_record(
    kind: str,
    username: str,
    beamline: str,
    pgroup: str,
    pattern: str,
    real_delete: bool,
) -> str:
    job_id = str(uuid.uuid4())[:8]
    record = {
        'job_id': job_id,
        'kind': kind,
        'username': username,
        'beamline': beamline,
        'pgroup': pgroup,
        'pattern': pattern,
        'real_delete': real_delete,
        'status': 'queued',
        'result': '',
        'created_at': _now(),
        'started_at': '',
        'finished_at': '',
    }
    with _jobs_lock:
        _jobs[job_id] = record
    return job_id


async def run_cleanup_job(
    job_id: str,
    beamline: str,
    pgroup: str,
    pattern: str,
    real_delete: bool,
) -> None:
    _update_job(job_id, status='running', started_at=_now())

    try:
        output = await asyncio.to_thread(
            run_cleanup_command,
            beamline,
            pgroup,
            pattern,
            real_delete,
        )
        _update_job(
            job_id,
            status='done',
            result=output,
            finished_at=_now(),
        )
    except Exception as e:
        _update_job(
            job_id,
            status='failed',
            result=str(e),
            finished_at=_now(),
        )


def submit_cleanup_job(
    username: str,
    beamline: str,
    pgroup: str,
    pattern: str,
    real_delete: bool,
) -> str:
    job_id = create_job_record(
        kind='cleanup',
        username=username,
        beamline=beamline,
        pgroup=pgroup,
        pattern=pattern,
        real_delete=real_delete,
    )
    asyncio.create_task(run_cleanup_job(job_id, beamline, pgroup, pattern, real_delete))
    return job_id

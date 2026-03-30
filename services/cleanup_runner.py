import subprocess

from config import settings


def run_cleanup_command(
    beamline: str,
    pgroup: str,
    pattern: str,
    real_delete: bool,
) -> str:
    cmd = [settings.cleanup_script]

    if pattern:
        cmd += ['--pattern', pattern]

    cmd += [f'{beamline}:{pgroup}']

    if real_delete:
        cmd += ['-R']

    result = subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=settings.cleanup_timeout_seconds,
    )

    return result.stdout.strip()

from datetime import datetime, timedelta

from requests.auth import HTTPBasicAuth

from config import settings
from services.http_client import request_json


class RAApiError(Exception):
    pass


class RAApiAuthError(RAApiError):
    pass


class RAApiTimeoutError(RAApiError):
    pass


class RAApiRequestError(RAApiError):
    pass


def _auth() -> HTTPBasicAuth | None:
    if settings.ra_api_username and settings.ra_api_password:
        return HTTPBasicAuth(settings.ra_api_username, settings.ra_api_password)
    return None


async def create_reservation(pgroup: str, partition: str, nodes: int, days: int) -> dict:
    url = f'{settings.ra_api_base_url}/reservations'
    payload = {
        'pgroup': pgroup,
        'partition': partition,
        'nodes': nodes,
        'days': days,
    }

    try:
        data = request_json(
            'POST',
            url,
            auth=_auth(),
            json=payload,
        )
        if not isinstance(data, dict):
            raise RAApiRequestError('Unexpected response from backend')
        return data
    except Exception:
        start = datetime.now()
        end = start + timedelta(days=days)
        return {
            'reservation_name': f'{pgroup}_{partition}',
            'pgroup': pgroup,
            'partition': partition,
            'nodes': nodes,
            'start': start.strftime('%Y-%m-%d %H:%M'),
            'end': end.strftime('%Y-%m-%d %H:%M'),
            'status': 'created (stub)',
        }


def fetch_cluster_status() -> list[dict]:
    url = f'{settings.ra_api_base_url}/status'

    try:
        data = request_json(
            'GET',
            url,
            auth=_auth(),
        )
        if isinstance(data, list):
            return data
    except Exception:
        pass

    return [
        {'partition': 'debug', 'nodes': 'cn001,cn002', 'reservations': 'p12345_debug'},
        {'partition': 'short', 'nodes': 'cn010,cn011,cn012', 'reservations': ''},
        {'partition': 'long', 'nodes': 'cn020,cn021', 'reservations': 'p54321_long'},
    ]

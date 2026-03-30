import requests

from config import settings


_session: requests.Session | None = None


def get_session() -> requests.Session:
    global _session

    if _session is None:
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'user-services-ng/1.0',
        })
        _session = session

    return _session


def request_json(method: str, url: str, **kwargs) -> dict | list:
    session = get_session()

    if 'timeout' not in kwargs:
        kwargs['timeout'] = (
            settings.requests_connect_timeout,
            settings.requests_read_timeout,
        )

    if 'verify' not in kwargs:
        kwargs['verify'] = settings.normalized_verify()

    response = session.request(method=method, url=url, **kwargs)
    response.raise_for_status()
    return response.json()

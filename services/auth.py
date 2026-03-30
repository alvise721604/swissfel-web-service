from fastapi import Request

from config import settings


def get_current_username(request: Request) -> str:
    header_name = settings.trusted_user_header.lower()

    for key, value in request.headers.items():
        if key.lower() == header_name:
            candidate = value.strip()
            return candidate or 'unknown'

    return 'unknown'

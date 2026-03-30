from dataclasses import dataclass, field
import os


@dataclass
class Settings:
    app_title: str = 'User Services'

    host: str = '127.0.0.1' #os.getenv('HOST', '127.0.0.1')
    port: int = 8080#int(os.getenv('PORT', '8080'))

    allowed_partitions: list[str] = field(default_factory=lambda: ['debug', 'short', 'long'])
    min_nodes: int = 1
    max_nodes: int = 10
    min_days: int = 1
    max_days: int = 30

    #ra_api_base_url: str = os.getenv('RA_API_BASE_URL', 'https://ra-s-004.psi.ch/compute/clusters/ra')
    ra_api_base_url: str = os.getenv('RA_API_BASE_URL', 'http://localhost:8000/compute/clusters/ra')
    ra_api_username: str = os.getenv('RA_API_USERNAME', '')
    ra_api_password: str = os.getenv('RA_API_PASSWORD', '')

    requests_connect_timeout: int = int(os.getenv('REQUESTS_CONNECT_TIMEOUT', '5'))
    requests_read_timeout: int = int(os.getenv('REQUESTS_READ_TIMEOUT', '30'))

    requests_verify: str | bool = os.getenv('REQUESTS_VERIFY', 'true')

    cleanup_script: str = os.getenv(
        'CLEANUP_SCRIPT',
        '/usr/local/user-services/pgroup_delete.py',
    )
    cleanup_timeout_seconds: int = int(os.getenv('CLEANUP_TIMEOUT_SECONDS', '3600'))

    trusted_user_header: str = os.getenv('TRUSTED_USER_HEADER', 'x-remote-user')
    mail_recipients: str = os.getenv('MAIL_RECIPIENTS', '')

    def normalized_verify(self) -> str | bool:
        value = self.requests_verify
        if isinstance(value, bool):
            return value
        low = str(value).strip().lower()
        if low in ('true', 'yes', '1'):
            return True
        if low in ('false', 'no', '0'):
            return False
        return str(value)


settings = Settings()

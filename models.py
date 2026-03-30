import re
from dataclasses import dataclass


PGROUP_RE = re.compile(r'^p\d{5,}$')
BEAMLINE_RE = re.compile(r'^[A-Za-z0-9_-]+$')


@dataclass
class ReservationForm:
    pgroup: str
    partition: str
    nodes: int
    days: int

    def validate(
        self,
        allowed_partitions: list[str],
        min_nodes: int,
        max_nodes: int,
        min_days: int,
        max_days: int,
    ) -> list[str]:
        errors: list[str] = []

        if not PGROUP_RE.fullmatch(self.pgroup):
            errors.append('Invalid PGROUP: expected format p12345')

        if self.partition not in allowed_partitions:
            errors.append('Invalid Partition')

        if not (min_nodes <= self.nodes <= max_nodes):
            errors.append(f'Number of nodes out of range ({min_nodes}-{max_nodes})')

        if not (min_days <= self.days <= max_days):
            errors.append(f'Number of days out of range ({min_days}-{max_days})')

        return errors


@dataclass
class CleanupForm:
    beamline: str
    pgroup: str
    pattern: str
    real_delete: bool

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.beamline.strip():
            errors.append('Beamline is mandatory')
        elif not BEAMLINE_RE.fullmatch(self.beamline):
            errors.append('Invalid beamline')

        if not PGROUP_RE.fullmatch(self.pgroup):
            errors.append('Invalid PGROUP: expected format p12345')

        return errors

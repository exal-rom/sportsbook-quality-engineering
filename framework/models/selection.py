from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Selection:
    selection_id: str
    odds: Decimal
    available: bool
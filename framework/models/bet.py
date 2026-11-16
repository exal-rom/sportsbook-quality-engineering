from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Bet:
    bet_id: str
    selection_id: str
    stake: Decimal
    odds: Decimal
    status: str
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Account:
    account_id: str
    available_balance: Decimal
    max_stake: Decimal
    max_liability: Decimal
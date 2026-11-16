from framework.models.selection import Selection
from decimal import Decimal
from framework.models.account import Account
from uuid import uuid4
from framework.models.bet import Bet
from framework.bet_repository import BetRepository


def validate_financial_conditions(
    account: Account,
    stake: Decimal,
    odds: Decimal
) -> bool:

    potential_liability = stake * (odds - Decimal("1"))

    return (
        stake > Decimal("0")
        and stake <= account.available_balance
        and stake <= account.max_stake
        and potential_liability <= account.max_liability
    )

def validate_selection(selection: Selection) -> bool:
    return selection.available

def can_place_bet(
    selection: Selection,
    account: Account,
    stake: Decimal
) -> bool:

    return (
        validate_selection(selection)
        and validate_financial_conditions(
            account,
            stake,
            selection.odds
        )
    )

def generate_bet_id() -> str:
    return str(uuid4())

def place_bet(
    selection: Selection,
    account: Account,
    stake: Decimal,
    repository: BetRepository,
    customer_id: str
) -> Bet | None:

    if not can_place_bet(selection, account, stake):
        return None

    bet = Bet(
        bet_id=generate_bet_id(),
        customer_id=customer_id,
        selection_id=selection.selection_id,
        stake=stake,
        odds=selection.odds,
        status="OPEN"
    )

    repository.save(bet)
    account.available_balance -= stake
    return bet
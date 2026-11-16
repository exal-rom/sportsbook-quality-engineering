from decimal import Decimal
from framework.models.bet import Bet


def test_create_open_bet():
    bet = Bet(
        bet_id="BET-001",
        selection_id="SEL-001",
        stake=Decimal("10.00"),
        odds=Decimal("2.50"),
        status="OPEN",
        customer_id="CUST-001",
    )

    assert bet.bet_id == "BET-001"
    assert bet.selection_id == "SEL-001"
    assert bet.stake == Decimal("10.00")
    assert bet.odds == Decimal("2.50")
    assert bet.status == "OPEN"
    assert bet.customer_id == "CUST-001"